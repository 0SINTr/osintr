from urllib.parse import urlparse
from fuzzywuzzy import fuzz
import spacy
import re

# Load spaCy's pre-trained NER model and download if not found
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_email_components(email):
    """Extract the username and domain from an email address."""
    try:
        username, domain = email.split('@')
    except ValueError:
        username, domain = email, ''
    return username, domain

def is_email(name):
    """Check if the given input is an email address."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", name) is not None

def is_username(name):
    """Check if the given input looks like a username."""
    # Assuming usernames are alphanumeric strings possibly containing underscores or hyphens
    return re.match(r"^[a-zA-Z0-9_.-]+$", name) is not None

def tokenize_username(username):
    """Tokenize username into meaningful parts."""
    # Split on letters and numbers
    tokens = re.findall(r'[A-Za-z]+|\d+', username)
    return tokens

def compute_similarity(name, text):
    """Compute similarity score using exact match and fuzzy logic."""
    if name == text:
        return 100  # Exact match
    else:
        return fuzz.partial_ratio(name, text)

def evaluate_urls(name, urls):
    """Evaluate relevance of URLs based on input name, email, or username."""
    results = []
    name_lower = name.lower()
    name_entity_label = None

    # Detect input type
    if is_email(name_lower):
        # Extract username and domain separately for emails
        username, domain = extract_email_components(name_lower)
        input_type = "email"
        tokens = tokenize_username(username)
    elif is_username(name_lower):
        input_type = "username"
        tokens = tokenize_username(name_lower)
    else:
        input_type = "name"
        tokens = name_lower.split()
        # Run NER on the input name to identify its type
        name_doc = nlp(name)
        for ent in name_doc.ents:
            if ent.text.lower() == name_lower and ent.label_ in ["PERSON", "ORG"]:
                name_entity_label = ent.label_
                break
        else:
            name_entity_label = None
        # Assign tokens if name input
        if not tokens:
            tokens = [name_lower]

    # Define stop words and excluded tokens
    stop_words = set([
        'the', 'of', 'and', 'in', 'to', 'a', 'for', 'on', 'at', 'by', 'with',
        'is', 'are', 'was', 'were', 'it', 'this', 'that', 'from', 'or', 'as',
        'an', 'be', 'but', 'not'
    ])

    # Process each URL
    for url in urls:
        score = 0
        exact_token_matches = 0
        partial_token_matches = 0

        url_domain = urlparse(url).netloc.lower()
        url_path = urlparse(url).path.lower()
        url_content = f"{url_domain} {url_path}"

        # Split URL content into words and filter out stop words
        url_words = [word for word in re.split(r'[\W_]+', url_content) if word and word not in stop_words]

        # Scoring based on input type
        if input_type == "email":
            # Exact match on username
            if username == url_domain or username in url_content:
                score += 100
                # print(f"Exact email match: '{username}' in URL '{url}'")
            else:
                username_similarity = compute_similarity(username, url_content)
                if username_similarity >= 60:
                    score += username_similarity * 0.7
                    # print(f"Partial email match: '{username}' similarity {username_similarity} in URL '{url}'")

            # Domain match
            if domain and domain in url_domain:
                score += 50
                # print(f"Domain match: '{domain}' in URL '{url}'")

            # Token matching
            for token in tokens:
                if token in stop_words:
                    # print(f"Excluded token '{token}' for URL '{url}'")
                    continue  # Skip excluded tokens
                for word in url_words:
                    if token == word:
                        exact_token_matches += 1
                        score += 20
                        # print(f"Exact token match: token '{token}' found in word '{word}' for URL '{url}'")
                        break
                    else:
                        token_similarity = compute_similarity(token, word)
                        # Adjusted similarity threshold to 70 and minimum token length to 4
                        if token_similarity >= 70 and len(token) >= 4:
                            partial_token_matches += 1
                            score += 15
                            # print(f"Partial token match: token '{token}' with word '{word}' similarity {token_similarity} for URL '{url}'")
                            break

        elif input_type == "username":
            if name_lower == url_domain or name_lower in url_content:
                score += 100  # Exact match
                # print(f"Exact username match: '{name_lower}' in URL '{url}'")
            else:
                # Partial and fuzzy matches
                name_similarity = compute_similarity(name_lower, url_content)
                if name_similarity >= 70:
                    score += name_similarity * 0.9
                    # print(f"Partial username match: '{name_lower}' similarity {name_similarity} in URL '{url}'")
                elif name_similarity >= 50:
                    score += name_similarity * 0.5
                    # print(f"Low partial username match: '{name_lower}' similarity {name_similarity} in URL '{url}'")

            # Token matching with URL words
            for token in tokens:
                if token in stop_words:
                    # print(f"Excluded token '{token}' for URL '{url}'")
                    continue  # Skip excluded tokens
                for word in url_words:
                    if token == word:
                        exact_token_matches += 1
                        score += 20
                        # print(f"Exact token match: token '{token}' found in word '{word}' for URL '{url}'")
                        break
                    else:
                        token_similarity = compute_similarity(token, word)
                        # Adjusted similarity threshold to 70 and minimum token length to 4
                        if token_similarity >= 70 and len(token) >= 4:
                            partial_token_matches += 1
                            score += 15
                            # print(f"Partial token match: token '{token}' with word '{word}' similarity {token_similarity} for URL '{url}'")
                            break

        else:  # input_type == "name"
            if name_lower in url_content:
                score += 100  # Exact full name match
                # print(f"Exact name match: '{name_lower}' in URL '{url}'")
            else:
                # Exact and partial token matches
                for token in tokens:
                    if token in stop_words:
                        # print(f"Excluded token '{token}' for URL '{url}'")
                        continue  # Skip excluded tokens
                    for word in url_words:
                        if token == word:
                            exact_token_matches += 1
                            score += 30
                            # print(f"Exact token match: token '{token}' found in word '{word}' for URL '{url}'")
                            break
                        else:
                            # Partial token matches
                            token_similarity = compute_similarity(token, word)
                            if token_similarity >= 70 and len(token) >= 4:
                                partial_token_matches += 1
                                score += 20
                                # print(f"Partial token match: token '{token}' with word '{word}' similarity {token_similarity} for URL '{url}'")
                                break

                # NER-based matching
                url_doc = nlp(url_content)
                for ent in url_doc.ents:
                    if ent.text.lower() == name_lower:
                        score += 50
                        # print(f"Exact entity match: '{ent.text}' in URL '{url}'")
                    elif ent.text.lower() in tokens:
                        score += 25
                        # print(f"Token entity match: '{ent.text}' in URL '{url}'")

        # **Adjusted Penalty Logic**
        # Apply penalties only if there are no exact or partial token matches
        if exact_token_matches == 0 and partial_token_matches == 0:
            if score < 50:
                score = max(0, score - 30)
                # print(f"Penalty applied: score reduced by 30 to {score} for URL '{url}'")
            elif score < 100:
                score = max(0, score - 20)
                # print(f"Penalty applied: score reduced by 20 to {score} for URL '{url}'")

        # Ensure score is non-negative and rounded
        score = max(0, round(score, 2))

        # Store results with URL and score
        results.append((url, score))

    # Sort results by score in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    return results

def main():
    """Main function to execute the URL matching."""
    # Example usage with different inputs
    inputs = ["johndoe@example.com", "johndoe123", "Open AI", "Elon Musk"]
    urls = [
        "https://johndoe.com/",
        "https://example.com/john-doe-profile",
        "https://www.notrelatedsite.com",
        "https://github.com/johndoe123",
        "https://example.com/contact/jdoe",
        "https://linkedin.com/in/john-doe",
        "https://openai.com/research/",
        "https://openai-company.com/about",
        "https://en.wikipedia.org/wiki/OpenAI",
        "https://anotherexample.com/ceo-of-open-ai",
        "https://www.spacex.com",
    ]

    # Run the evaluation for each input
    for name in inputs:
        print(f"\nEvaluating URLs related to: {name}\n")
        related_urls = evaluate_urls(name, urls)
        for url, score in related_urls:
            print(f"URL: {url} - Relevance Score: {score}")

if __name__ == '__main__':
    main()