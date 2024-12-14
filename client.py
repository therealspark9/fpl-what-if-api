import requests

def main():
    # Prompt user to enter their team ID
    try:
        team_id = int(input("Enter your FPL Team ID: "))
    except ValueError:
        print("Invalid input. Please enter a numeric Team ID.")
        return

    # Prepare the POST request payload
    payload = {
        "teamId": team_id
    }

    # Define the Flask server URL
    url = "http://127.0.0.1:5000/calculate"

    try:
        # Send the POST request to the /calculate endpoint
        response = requests.post(url, json=payload)

        # Check for successful response
        if response.status_code == 200:
            data = response.json()

            # Display calculation results
            print("\nCalculation Results:")
            for key, value in data.items():
                print(f"{key}: {value}")

            # Display additional messages based on the response
            current_actual = data['currentActual']
            what_if_score = data['whatIfScore']
            highest_scorer = data['highestScorer']
            captain = data['captain']

            print("\nSummary:")
            print(f"Your current score is {current_actual}")
            print(f"Your What If score is {what_if_score}")
            print(f"You would have gotten {what_if_score - current_actual} points if you had not made any transfers")
            print(f"You should've captained {highest_scorer} instead of {captain}")

            if captain == highest_scorer:
                print("You actually picked the right captain, wow")
            else:
                print("You could've had more points, ouch")

            print("\nGood job :)")
        else:
            print(f"Error: Unable to calculate data (Status Code: {response.status_code}).")
            print("Response:", response.text)

    except requests.ConnectionError:
        print("Error: Unable to connect to the Flask server. Ensure it is running.")

if __name__ == "__main__":
    main()
