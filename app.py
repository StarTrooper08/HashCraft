import requests

url = "https://gql.hashnode.com/"  # GraphQL endpoint URL

# Define your GraphQL query
query = """
query Publication {
  publication(host: "atharva08.hashnode.dev") {
    isTeam
    title
    post(slug: "efficiency-unleashed-dockerizing-and-optimizing-a-fastapi-app-with-slimtoolkit-and-github-actions") {
      title
      content {
        html
      }
    }
  }
}
"""

# Prepare the request payload
data = {"query": query}

# Make the GraphQL request
response = requests.post(url, json=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    result = response.json()
    print(result)
else:
    print(f"GraphQL request failed with status code {response.status_code}: {response.text}")