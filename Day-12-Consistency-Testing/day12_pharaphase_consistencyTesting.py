
import requests
import json
from datetime import datetime

URL = "http://localhost:11434/api/generate"


# Function 1: Call Ollama
def call_ollama(question):

    payload = {
        "model": "qwen2.5:3b",
        "prompt": question,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    response = requests.post(
        URL,
        json=payload,
        timeout=(10, 300)
    )

    response.raise_for_status()

    return response.json()["response"]


# Function 2: Generate repeated responses
def generate_responses(question, num_responses):

    responses = []

    for i in range(num_responses):

        actual = call_ollama(question)

        responses.append(actual)

    return responses


# Function 3: Validate textual consistency
def validate_textual_consistency(responses):

    if not isinstance(responses, list) or not responses:
        return "REVIEW"

    normalized_responses = []

    for response in responses:

        if not isinstance(response, str) or not response.strip():
            return "REVIEW"

        cleaned_response = response.lower().strip()

        normalized_responses.append(cleaned_response)

    if len(set(normalized_responses)) == 1:
        return "CONSISTENT"

    else:
        return "INCONSISTENT"


# Function 4: Generate paraphrase responses
def generate_paraphrase_responses(questions):

    responses = []

    for question in questions:

        actual = call_ollama(question)

        responses.append(actual)

    return responses


# Function 5: Evaluate semantic consistency
def evaluate_paraphrase_consistency(questions, responses):

    if not isinstance(questions, list) or not isinstance(responses, list):
        return "REVIEW"

    if len(questions) != len(responses) or len(questions) < 2:
        return "REVIEW"

    if any(not isinstance(q, str) or not q.strip() for q in questions):
        return "REVIEW"

    if any(not isinstance(r, str) or not r.strip() for r in responses):
        return "REVIEW"

    judge_prompt = f"""
    You are an AI testing evaluator.

    Compare the following questions and AI responses.

    Questions:
    {questions}

    Responses:
    {responses}

    Check whether all responses communicate
    the same key facts.

    Different wording is acceptable.
    Contradictory facts are not acceptable.

    Return only one of these exact words:

    CONSISTENT
    INCONSISTENT
    """

    result = call_ollama(judge_prompt)

    # Advanced validation: Check judge response
    if not isinstance(result, str) or not result.strip():
        return "REVIEW"

    result = result.strip().upper()

    if result == "CONSISTENT":
        return "CONSISTENT"

    elif result == "INCONSISTENT":
        return "INCONSISTENT"

    else:
        return "REVIEW"


# Main execution

test_results = []
passed = 0
failed = 0
review = 0
invalid = 0
errors = 0

try:

    with open("day12_pharaphase_consistency_testing.json", "r") as file:

        test_cases = json.load(file)

    if not isinstance(test_cases, list) or not test_cases:
        raise ValueError("Test data must be a non-empty JSON list")

    for test_case in test_cases:

        print("\n================================")

        try:

            if not isinstance(test_case, dict):
                raise ValueError("Test case must be a JSON object")

            test_id = test_case["test_id"]
            test_type = test_case["test_type"]

            # Advanced validation: Check test ID
            if not isinstance(test_id, str) or not test_id.strip():
                raise ValueError("Invalid test ID")

            # Advanced validation: Check test type
            if not isinstance(test_type, str) or not test_type.strip():
                raise ValueError("Invalid test type")

            print("Test ID:", test_id)
            print("Test Type:", test_type)

            # Repeated prompt testing
            if test_type == "repeated":

                question = test_case["question"]
                num_responses = test_case["num_responses"]

                if not isinstance(question, str) or not question.strip():
                    raise ValueError("Invalid question")

                if type(num_responses) != int or num_responses < 2:
                    raise ValueError("num_responses must be an integer of at least 2")

                print("Question:", question)

                responses = generate_responses(
                    question, num_responses
                )

                for index, actual in enumerate(responses, start=1):

                    print(f"\nResponse {index}:")
                    print(actual)

                result = validate_textual_consistency(responses)

            # Paraphrase consistency testing
            elif test_type == "paraphrase":

                questions = test_case["questions"]

                if not isinstance(questions, list) or len(questions) < 2:
                    raise ValueError("At least two paraphrase questions are required")

                if any(not isinstance(q, str) or not q.strip() for q in questions):
                    raise ValueError("Invalid paraphrase question")

                responses = generate_paraphrase_responses(questions)

                for index, (question, actual) in enumerate(
                    zip(questions, responses), start=1
                ):

                    print(f"\nQuestion {index}:")
                    print(question)

                    print(f"Response {index}:")
                    print(actual)

                result = evaluate_paraphrase_consistency(
                    questions, responses
                )

            else:

                raise ValueError("Unknown test type")

            print("\nConsistency Result:", result)
            if test_type == "repeated":

                report_questions = [question]

            else:

                report_questions = questions


            test_result = {
                "test_id": test_id,
                "test_type": test_type,
                "questions": report_questions,
                "responses": responses,
                "result": result
            }

            test_results.append(test_result)

            if result == "CONSISTENT":
                passed += 1

            elif result == "INCONSISTENT":
                failed += 1

            else:
                review += 1

        except ValueError as e:

            print("INVALID TEST DATA:", e)
            invalid += 1

        except KeyError as e:

            print("INVALID: Missing JSON field:", e)
            invalid += 1

        except requests.exceptions.RequestException as e:

            print("ERROR: Ollama API issue:", e)
            errors += 1

        # Advanced error handling
        except Exception as e:

            print("UNEXPECTED ERROR:", e)
            errors += 1

        print("================================")


except FileNotFoundError:

    print("ERROR: JSON test data file not found")

except json.JSONDecodeError:

    print("ERROR: Invalid JSON format")

except ValueError as e:

    print("ERROR:", e)


# Final execution summary
print("\n========== EXECUTION SUMMARY ==========")

print("Total Passed:", passed)
print("Total Failed:", failed)
print("Total Review:", review)
print("Total Invalid:", invalid)
print("Total Errors:", errors)

total = passed + failed + review + invalid + errors
execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
report = {
    "execution_time": execution_time,
    "total_tests": total,
    "passed": passed,
    "failed": failed,
    "review": review,
    "invalid": invalid,
    "errors": errors,
    "test_results": test_results
}

with open("consistency_report.json", "w") as file:

    json.dump(report, file, indent=4)

print("\nJSON report generated successfully!")

print("Total Test Cases:", total)

print("=======================================")
