import re
import itertools
from difflib import SequenceMatcher

# Try to import external libraries; if unavailable, handle accordingly
try:
    import jellyfish  # For phonetic matching
except ImportError:
    jellyfish = None

try:
    import Levenshtein  # For efficient Levenshtein distance calculation
except ImportError:
    Levenshtein = None

try:
    from homoglyphs import Homoglyphs  # For homoglyph normalization
except ImportError:
    Homoglyphs = None

EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)

def is_valid_email(email):
    """Validate email address format."""
    return re.match(EMAIL_REGEX, email) is not None

def filter_valid_emails(email_list):
    """Filter out invalid email addresses from the list."""
    return [email for email in email_list if is_valid_email(email)]

def exact_match(input_email, email_list):
    """Exact email match."""
    return [email for email in email_list if email == input_email]

def case_insensitive_match(input_email, email_list):
    """Case-insensitive email match."""
    input_email_lower = input_email.lower()
    return [email for email in email_list if email.lower() == input_email_lower]

def normalize_email(email):
    """Normalize email by handling plus-addressing."""
    local_part, domain = email.lower().split('@')
    local_part = local_part.split('+')[0]
    return f"{local_part}@{domain}"

def normalization_match(input_email, email_list):
    """Match emails after normalization."""
    normalized_input = normalize_email(input_email)
    return [email for email in email_list if normalize_email(email) == normalized_input]

def get_char_mapping():
    """Return a mapping of characters to their possible replacements."""
    char_mapping = {
        '1': ['1', 'i', 'l'],
        'i': ['i', '1', 'l'],
        'l': ['l', '1', 'i'],
        '0': ['0', 'o'],
        'o': ['o', '0'],
        '3': ['3', 'e'],
        'e': ['e', '3'],
        '5': ['5', 's'],
        's': ['s', '5'],
        '7': ['7', 't'],
        't': ['t', '7'],
        '2': ['2', 'z'],
        'z': ['z', '2'],
        '4': ['4', 'a'],
        'a': ['a', '4'],
        '6': ['6', 'b'],
        '9': ['9', 'g'],
        'g': ['g', '9'],
        '8': ['8', 'b'],
        'b': ['b', '6', '8'],
    }
    return char_mapping

def generate_variations(text, char_mapping):
    """Generate all possible variations of the text based on the character mapping."""
    text = text.lower()
    chars = list(text)
    positions = []

    # Identify positions of characters that have multiple mappings
    for index, char in enumerate(chars):
        if char in char_mapping:
            positions.append((index, char_mapping[char]))

    # If there are no characters to replace, return the original text
    if not positions:
        return [text]

    # Generate all combinations of replacements
    variations = set()
    replacement_options = [replacements for index, replacements in positions]
    for replacements in itertools.product(*replacement_options):
        temp_chars = chars.copy()
        for (index, _), replacement_char in zip(positions, replacements):
            temp_chars[index] = replacement_char
        variation = ''.join(temp_chars)
        variations.add(variation)

    # Include the original text
    variations.add(text)

    return list(variations)

def normalize_local_part(local_part):
    """Normalize local part by removing dots and plus-addressing."""
    # Remove plus-addressing
    local_part = local_part.split('+')[0]
    # Remove dots
    local_part = local_part.replace('.', '')
    return local_part

def levenshtein_match(input_email, email_list, threshold=2):
    """Fuzzy match emails using Levenshtein distance on generated variations."""
    matches = []
    input_local = input_email.lower().split('@')[0]
    char_mapping = get_char_mapping()
    input_variations = generate_variations(input_local, char_mapping)
    input_variations = set(normalize_local_part(var) for var in input_variations)

    for email in email_list:
        local_part = email.lower().split('@')[0]
        local_variations = generate_variations(local_part, char_mapping)
        local_variations = set(normalize_local_part(var) for var in local_variations)

        # Compute the minimum Levenshtein distance between any variation pairs
        min_distance = float('inf')
        for input_var in input_variations:
            for local_var in local_variations:
                if Levenshtein:
                    distance = Levenshtein.distance(local_var, input_var)
                else:
                    seq_matcher = SequenceMatcher(None, local_var, input_var)
                    distance = int((1 - seq_matcher.ratio()) * max(len(local_var), len(input_var)))
                if distance < min_distance:
                    min_distance = distance
        if min_distance <= threshold:
            matches.append(email)
    return matches

def character_variation_match(input_email, email_list):
    """Match emails by generating variations based on character mappings."""
    char_mapping = get_char_mapping()
    input_variations = generate_variations(input_email.lower(), char_mapping)
    input_variations_set = set(input_variations)

    matches = []
    for email in email_list:
        email_variations = generate_variations(email.lower(), char_mapping)
        if input_variations_set.intersection(email_variations):
            matches.append(email)
    return matches

def homoglyph_match(input_email, email_list):
    """Match emails after normalizing homoglyphs."""
    if not Homoglyphs:
        return []  # Can't perform homoglyph matching without the homoglyphs package
    homoglyphs = Homoglyphs()
    normalized_input = homoglyphs.to_ascii(input_email)
    return [email for email in email_list if homoglyphs.to_ascii(email) == normalized_input]

def domain_variation_match(input_email, email_list, threshold=1):
    """Match emails with similar domain names."""
    input_domain = input_email.lower().split('@')[1]
    matches = []
    for email in email_list:
        domain = email.lower().split('@')[1]
        if Levenshtein:
            distance = Levenshtein.distance(domain, input_domain)
        else:
            seq_matcher = SequenceMatcher(None, domain, input_domain)
            distance = int((1 - seq_matcher.ratio()) * max(len(domain), len(input_domain)))
        if distance <= threshold:
            matches.append(email)
    return matches

def phonetic_match(input_email, email_list):
    """Phonetic matching using Metaphone algorithm."""
    if not jellyfish:
        return []  # Can't perform phonetic matching without jellyfish
    input_local = input_email.split('@')[0]
    input_phonetic = jellyfish.metaphone(input_local)
    return [email for email in email_list if jellyfish.metaphone(email.split('@')[0]) == input_phonetic]

def substring_match(input_email, email_list):
    """Match emails where one is a substring of the other."""
    input_email_lower = input_email.lower()
    return [email for email in email_list if input_email_lower in email.lower() or email.lower() in input_email_lower]

def regex_match(input_email, email_list):
    """Match emails using regex patterns."""
    pattern_str = re.escape(input_email).replace(r'\*', '.*').replace(r'\?', '.')
    pattern = re.compile(pattern_str, re.IGNORECASE)
    return [email for email in email_list if pattern.match(email)]

def match_emails(target_email, email_list):
    """Combine matching methods to find related emails."""
    matches_set = set()

    # Only proceed if target_email is a valid email
    if not is_valid_email(target_email):
        return []

    # Apply matching methods
    matches_set.update(normalization_match(target_email, email_list))
    matches_set.update(levenshtein_match(target_email, email_list))
    matches_set.update(character_variation_match(target_email, email_list))
    matches_set.update(homoglyph_match(target_email, email_list))
    matches_set.update(domain_variation_match(target_email, email_list))
    matches_set.update(phonetic_match(target_email, email_list))
    matches_set.update(substring_match(target_email, email_list))
    matches_set.update(regex_match(target_email, email_list))

    return list(matches_set)

def main():
    """Main function to execute the email matching."""
    # Input email address
    input_email = 'example.email+test@gmail.com'

    # List of emails to check against
    email_list = [
        'exampleemail@gmail.com',
        'example.email@gmail.com',
        'examp1e.email@gmail.com',
        'exampleemail+spam@gmail.com',
        'examp1e.emai1@gmail.com',
        'user@gnail.com',
        'example-email@gmail.com',
        'example.email@googlemail.com',
        'example_email@yahoo.com',
        'exampl3.email@gmail.com',
        'examp1e.emai1@gnail.com',
        'us3r@example.com',      # Added for testing leet replacements
        'john$doe@example.com',  # Testing with a valid special character
        'invalid@exa@mple.com',  # Invalid email address
    ]

    # Filter out invalid emails
    email_list = filter_valid_emails(email_list)

    # Find related emails using combined methods
    matches = match_emails(input_email, email_list)

    # Output the results
    print(f"Input Email: {input_email}\n")
    print("Related Emails Found:")
    for email in matches:
        print(f"- {email}")

if __name__ == '__main__':
    main()