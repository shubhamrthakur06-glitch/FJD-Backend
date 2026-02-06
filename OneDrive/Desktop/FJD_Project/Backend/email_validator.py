import re
import Levenshtein  # pip install python-Levenshtein
import dns.resolver

class EmailValidator:
    def __init__(self):
        # LAYER 1: THE FREE LOADER LIST
        # Real companies do not use these.
        self.free_providers = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "rediffmail.com", "aol.com", "icloud.com", "protonmail.com",
            "yandex.com", "zoho.com", "mail.com", "gmx.com"
        }

        # LAYER 2: SCAMMER GRAMMAR (Username Patterns)
        # Real people use names (shubham.s). Scammers use titles.
        self.suspicious_keywords = [
            "hr", "hiring", "manager", "recruit", "team", "desk", 
            "career", "job", "offer", "support", "admin", "dept", 
            "official", "work", "verify"
        ]

    def _extract_domain(self, email):
        """Helper to get 'gmail.com' from 'john@gmail.com'"""
        try:
            return email.split('@')[1].lower().strip()
        except IndexError:
            return None

    def _extract_username(self, email):
        """Helper to get 'john' from 'john@gmail.com'"""
        try:
            return email.split('@')[0].lower().strip()
        except IndexError:
            return None

    def _extract_company_name_from_text(self, text):
        """
        Layer 3 Helper: Tries to guess the company name from the email body.
        Looks for patterns like 'Greetings from Amazon' or 'Hiring at Google'.
        """
        # Regex to find "At [Company]" or "From [Company]"
        patterns = [
            r"from\s+([A-Z][a-zA-Z0-9]+)",  # Matches "from Amazon"
            r"at\s+([A-Z][a-zA-Z0-9]+)",    # Matches "at Google"
            r"joining\s+([A-Z][a-zA-Z0-9]+)" # Matches "joining Microsoft"
        ]
        
        candidates = []
        for p in patterns:
            matches = re.findall(p, text)
            candidates.extend(matches)
        
        # Return the most likely company name (if found), else None
        return candidates[0].lower() if candidates else None
    
    def _check_domain_exists(self, domain):
        """Layer 4 Helper: Pings DNS to see if domain is real."""
        try:
            dns.resolver.resolve(domain, 'MX') # Checks for Mail Server
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
            return False

    def validate(self, email, body_text):
        """
        MASTER FUNCTION: Returns (Identity Score, Reason, Verdict)
        Score starts at 100 (Trusted) and drops based on red flags.
        """
        score = 100
        reasons = []
        domain = self._extract_domain(email)
        username = self._extract_username(email)

        if not domain or not username:
            return 0, ["Invalid Email Format"], "INVALID"

        # ---------------------------------------------------------
        # 🛡️ LAYER 1: THE FREE LOADER CHECK (Instant Kill)
        # ---------------------------------------------------------
        if domain in self.free_providers:
            # CHECK EXCEPTION: If the body mentions "Hiring" or "Job"
            # and sender is Gmail -> IT IS A SCAM.
            keywords = ["hiring", "job", "offer", "interview", "salary", "recruit"]
            if any(k in body_text.lower() for k in keywords):
                score -= 100
                reasons.append(f"Corporate hiring via Free Email ({domain})")
            else:
                score -= 50 # Just a personal email, mostly safe but not "Verified"
                reasons.append(f"Sent from Free Provider ({domain})")

        # ---------------------------------------------------------
        # 🕵️ LAYER 2: THE PATTERN DETECTIVE (Behavioral)
        # ---------------------------------------------------------
        # Count how many corporate words are in the username (e.g. "hr-manager-hiring")
        keyword_hits = 0
        for word in self.suspicious_keywords:
            if word in username:
                keyword_hits += 1
        
        if keyword_hits >= 2:
            score -= 40
            reasons.append(f"Suspicious Username Pattern ('{username}')")
        elif keyword_hits == 1 and domain in self.free_providers:
            score -= 50 # "hr@gmail.com" -> FATAL
            reasons.append("Generic HR Title on Free Email")

        # ---------------------------------------------------------
        # 🔢 LAYER 3: TYPOSQUATTING (The Math Check)
        # ---------------------------------------------------------
        claimed_company = self._extract_company_name_from_text(body_text)
        
        if claimed_company and domain not in self.free_providers:
            # Remove the .com/.net from domain to compare names
            domain_name = domain.split('.')[0]
            
            # Calculate Similarity (0 to 100)
            similarity = Levenshtein.ratio(claimed_company, domain_name) * 100
            
            # SCAM LOGIC:
            # If claimed is "Amazon" and domain is "Amaz0n" (Similarity > 80% but not 100%)
            # SCAM LOGIC (With DNS Check):
            if 80 < similarity < 100:
                # Critical Check: Is it a Hacker or a Blur?
                if self._check_domain_exists(domain):
                    # Domain EXISTS -> It is a Scammer who bought amaz0n.com
                    score -= 80
                    reasons.append(f"🚨 SPOOFING CONFIRMED: Fake domain '{domain}' is active.")
                else:
                    # Domain DEAD -> It is likely an OCR/Camera Error (amazqn.com)
                    # We do NOT punish the score. We just warn.
                    reasons.append(f"⚠️ OCR WARNING: Domain '{domain}' is unreachable. Verify manually.")
            
            # SAFE LOGIC:
            # If claimed is "Amazon" and domain is "Amazon" (Similarity 100%)
            elif similarity == 100:
                score += 20 # Bonus trust
                reasons.append(f"Domain matches Company Name ('{claimed_company}')")

        # ---------------------------------------------------------
        # ⚖️ FINAL VERDICT CALCULATION
        # ---------------------------------------------------------
        score = max(0, min(100, score)) # Clamp between 0 and 100
        
        if score == 0:
            verdict = "FATAL 🔴"
        elif score < 50:
            verdict = "SUSPICIOUS 🟡"
        elif score < 80:
            verdict = "NEUTRAL ⚪"
        else:
            verdict = "VERIFIED 🟢"

        return score, reasons, verdict
