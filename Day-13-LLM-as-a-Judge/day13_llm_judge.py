
import requests
import json
from datetime import datetime

URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5:3b"


# Function 1: Call Ollama
def call_ollama(prompt, response_format=None):

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    if response_format:
        payload["format"] = response_format

    response = requests.post(
        URL,
        json=payload,
        timeout=(10, 300)
    )

    response.raise_for_status()

    return response.json()["response"]


# Function 2: Generate AI response
def generate_response(question):

    prompt = f"""
    Answer the following question clearly and accurately.

    Question: {question}
    """

    actual_response = call_ollama(prompt)

    return actual_response


# Function 3: Evaluate response using LLM Judge
# Function 3: Evaluate response using LLM Judge
def evaluate_response(question, actual_response, required_elements):

    judge_prompt = f"""
    You are an expert AI response evaluator.

    Evaluate the AI-generated response using these four criteria:

    1. Relevance:
       Does the response answer the original question?

    2. Accuracy:
       Is the information factually correct?

    3. Completeness:
       Does the response cover all required elements?
       Accept semantically equivalent wording.
       Do not require exact keyword matches.

    4. Clarity:
       Is the response easy to understand?

    Important evaluation rules:

    - Evaluate the actual meaning of the response.
    - Do not penalize equivalent phrases.
    - Do not invent missing requirements.
    - Give credit for every required element that is
      clearly covered, even if different words are used.
    - Do not give a score of 1 when the response
      correctly covers most requirements.
    - Explain exactly which required elements are missing.

    ORIGINAL QUESTION:
    {question}

    AI-GENERATED RESPONSE:
    {actual_response}

    REQUIRED ELEMENTS:
    {json.dumps(required_elements, indent=4)}

    Give each criterion a score between 1 and 5.

    Scoring guide:
    1 = Very Poor
    2 = Poor
    3 = Average
    4 = Good
    5 = Excellent

    Overall score MUST equal the arithmetic average
    of the four criterion scores, rounded to two decimals.

    Return ONLY this exact flat JSON structure.
    Do not use nested objects or a criteria array.

    {{
        "relevance": 5,
        "accuracy": 5,
        "completeness": 5,
        "clarity": 5,
        "overall_score": 5.0,
        "reason": "Explain the evaluation and identify missing elements."
    }}

    All six fields are mandatory.
    Individual scores must be integers from 1 to 5.
    Overall score must be a number from 1 to 5.
    Reason must be a non-empty string.
    Return only valid JSON without Markdown.
    """

    judge_response = call_ollama(
        judge_prompt,
        response_format="json"
    )

    return judge_response

# Function 4: Parse Judge JSON response
def parse_judge_response(judge_response):

    try:
        result = json.loads(judge_response)

        return result

    except json.JSONDecodeError:

        print("ERROR: Judge returned invalid JSON")

        return None


# Function 5: Validate Judge scores
def validate_judge_scores(result):

    required_fields = [
        "relevance",
        "accuracy",
        "completeness",
        "clarity",
        "overall_score",
        "reason"
    ]

    if not isinstance(result, dict):
        return False

    for field in required_fields:

        if field not in result:
            print("Missing field:", field)
            return False

    score_fields = [
        "relevance",
        "accuracy",
        "completeness",
        "clarity"
    ]

    for field in score_fields:

        score = result[field]

        if (
            not isinstance(score, int)
            or isinstance(score, bool)
            or not 1 <= score <= 5
        ):

            print("Invalid score:", field, score)

            return False

    overall = result["overall_score"]

    if isinstance(overall, bool) or not isinstance(overall, (int, float)):

        print("Invalid overall score")

        return False

    if not 1 <= overall <= 5:

        print("Invalid overall score")

        return False

    if not isinstance(result["reason"], str) or not result["reason"].strip():

        print("Invalid evaluation reason")

        return False

    return True


# Function 6: Validate overall score calculation
def validate_overall_score(result):

    scores = [
        result["relevance"],
        result["accuracy"],
        result["completeness"],
        result["clarity"]
    ]

    calculated_average = round(sum(scores) / len(scores), 2)

    judge_score = result["overall_score"]

    if abs(judge_score - calculated_average) > 0.01:

        print("Judge score mismatch!")

        print("Judge Score:", judge_score)

        print("Calculated Score:", calculated_average)

        return False

    return True


# Function 7: Validate test case input
def validate_test_case(test_case):

    if not isinstance(test_case, dict):
        raise ValueError("Test case must be a JSON object")

    test_id = test_case.get("test_id")

    question = test_case.get("question")

    required_elements = test_case.get("required_elements")

    if not isinstance(test_id, str) or not test_id.strip():
        raise ValueError("Invalid or missing test ID")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Invalid or missing question")

    if (
        not isinstance(required_elements, list)
        or not required_elements
        or any(not isinstance(item, str) or not item.strip()
               for item in required_elements)
    ):
        raise ValueError("Invalid required elements")

    return test_id, question, required_elements


# Main execution
if __name__ == "__main__":

    passed = 0
    failed = 0
    review = 0
    errors = 0

    test_results = []

    try:

        with open("day13_judge_test_cases.json", "r") as file:

            test_cases = json.load(file)

        if not isinstance(test_cases, list) or not test_cases:

            raise ValueError("Test data must be a non-empty JSON list")

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:

        print("TEST DATA ERROR:", e)

        raise SystemExit(1)

    for test_case in test_cases:

        test_id = "UNKNOWN"
        question = "UNKNOWN"

        print("\n==============================")

        try:

            # Step 1: Validate test data
            test_id, question, required_elements = validate_test_case(test_case)

            print("Test ID:", test_id)
            print("Question:", question)

            # Step 2: Generate AI response
            actual_response = generate_response(question)

            print("\nGenerated Response:")
            print(actual_response)

            # Step 3: Evaluate using LLM Judge
            judge_response = evaluate_response(
                question,
                actual_response,
                required_elements
            )

            # Step 4: Parse Judge JSON
            result = parse_judge_response(judge_response)

            # Step 5: Validate scores
            if (
                result is None
                or not validate_judge_scores(result)
                or not validate_overall_score(result)
            ):

                test_status = "REVIEW"
                review += 1

            else:

                print("\nJudge Evaluation:")
                print(json.dumps(result, indent=4))

                if result["overall_score"] >= 4:

                    test_status = "PASS"
                    passed += 1

                else:

                    test_status = "FAIL"
                    failed += 1

            # Step 6: Store test result
            test_results.append({
                "test_id": test_id,
                "question": question,
                "generated_response": actual_response,
                "judge_evaluation": result,
                "status": test_status
            })

            print("\nTest Status:", test_status)

        except ValueError as e:

            print("INVALID TEST DATA:", e)

            invalid_status = "INVALID"

            test_results.append({
                "test_id": test_id,
                "question": question,
                "status": invalid_status,
                "error": str(e)
            })

            # Invalid is tracked separately from API errors
            invalid = sum(
                1 for item in test_results
                if item["status"] == "INVALID"
            )

        except requests.RequestException as e:

            print("API ERROR:", e)

            errors += 1

            test_results.append({
                "test_id": test_id,
                "question": question,
                "status": "ERROR",
                "error": str(e)
            })

        except Exception as e:

            print("UNEXPECTED ERROR:", e)

            errors += 1

            test_results.append({
                "test_id": test_id,
                "question": question,
                "status": "ERROR",
                "error": str(e)
            })

        print("==============================")

    # Step 7: Execution summary

    invalid = sum(
        1 for item in test_results
        if item["status"] == "INVALID"
    )

    total = passed + failed + review + invalid + errors

    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n========== EXECUTION SUMMARY ==========")

    print("Total Tests:", total)
    print("Passed:", passed)
    print("Failed:", failed)
    print("Review:", review)
    print("Invalid:", invalid)
    print("Errors:", errors)

    # Step 8: Generate JSON execution report

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

    with open("day13_judge_execution_report.json", "w") as file:

        json.dump(report, file, indent=4)

    print("\nExecution report generated successfully!")

    print("=======================================")
