from openai import OpenAI
import os
import json

def strings_to_object_names(strings):
  object_names = []
  for string in strings:
    object_name = string
    object_names.append(object_name)
  return object_names



def openai_api(system_message, user_message, context_data=None, tools=None):
    messages = [{"role": "system", "content": system_message}]
    toolsx=[]
    # if context_data is provided, add it to the conversation, if its a dictionary turn it to a string   
        
    if context_data:
        if isinstance(context_data, dict):
            context_str = json.dumps(context_data, indent=2)  # Format dict as JSON
        elif isinstance(context_data, str):
            context_str = context_data
        else:
            print("Context data must be a dictionary or a string.")
            return None
        messages.append({"role": "user", "content": f"Context Data:\n{context_str}"})
    
    # if no context data is provided, add the user message to the conversation
    messages.append({"role": "user", "content": user_message})

    # if tools are provided, call the API with tools
    try:
        if tools:
            client = OpenAI(api_key = "Enter your API key here")
            response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
            )
            reply = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls
            #print("tool call from LLM -----",tool_calls)
            #print("message reponse from LLM -------------- ", response.choices[0].message)
            #print("actual message ---------------",messages)
            
            
            if tool_calls:
                print("Tool call detected")
                print()  # Print an empty line
                print()  # Print an empty line
                
                print()  # Print an empty line
                #print("reply with tool call ", reply)
                print()  # Print an empty line
                
                tool_call_id = tool_calls[0].id
                tool_function_name = tool_calls[0].function.name
                #tool_query_string = json.loads(tool_calls[0].function.arguments)['query']
                
                # Step 3: call the function
                available_functions = {
                    "get_current_weather": "get_current_weather",
                    "script_gen": "script_gen",
                    "write_script": "write_script"
                }  
                # only one function in this example, but you can have multiple
        
                messages.append(response.choices[0].message)    # extend conversation with assistant's reply
                print()  # Print an empty line
                #print("Input1 message for tool is ....",messages) 
                print()
                # Step 4: send the info for each function call and function response to the model
                for tool_call in tool_calls:
                    print("for each tool call",tool_call)
                    function_name = tool_call.function.name # 'tool_calls' .function.name='get_online_data'
                    function_to_call = available_functions[function_name] # 'available_functions' = "get_online_data" [could be more than one function]
                    #function_args = json.loads(tool_call.function.arguments) # 'tool_call' .function.arguments='{"input":"latest news on israel"}'
                    #function_response = function_to_call(**function_args) # now call the function(s) with the arguments
                    #print("function name getting called ",function_name)
            
                    if function_name == "get_current_weather":
                        print("tool function name called  ",tool_function_name)
                        results = " -10 degrees celsius, and cold"
                        print (results)
                    
                    if function_name == 'write_script':
                        results = "the main focus is the cats were floating in the RIVER AS IT WAS raining in london"
                        print ("script gen reponed", results)
                    
                    if function_name == 'vvv':
                        results = " -10 degrees celsius, and cold"
                        print ("vvv",results)            
                    
                    
                    
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": results,
                        }
                    )
                    print()  # Print an empty line
                    #print("Input message for tool is ....",messages)                           
                    print()  # Print an empty line
                    
                        
                    client = OpenAI(api_key = "Enter your API key here")
                    tool_message = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                    )
                    print()  # Print an empty line
                    #print("LLM reply with tool..  ",tool_message.choices[0].message.content)
                    print()  # Print an empty line
                    return tool_message.choices[0].message.content
            
            else:
                print()  # Print an empty line
                #print("LLM replied ...",response.choices[0].message.content)
                print()  # Print an empty line
                return response.choices[0].message.content

        else:
            # if no tools are provided, call the API without tools
            client = OpenAI(api_key = "Enter your API key here")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            #print(" Api call with no tools",response.choices[0].message.content)
            return response.choices[0].message.content

    # if an error occurs, print the error message and return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


 
get_current_weather = {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }


write_script = {
  "type": "function",
  "function": {
    "name": "write_script",
    "description": "write a story based on the given topic",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city where the story is based"
        }
      },
      "required": ["location"]  # Add this line to make 'location' a required parameter
    }
  }
}

 
def load_agent_from_json(filepath):
    """Loads agent data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Agent file not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return None

def run_agent(agent_filepath, user_query, context_data=None):
    """Runs a single agent."""
    agent = load_agent_from_json(agent_filepath)
    if agent is None:
        return None

    system_instructions = agent.get("role", "You are a helpful assistant.") # Default role
    if "skills" in agent:
        system_instructions += f"\nYou have the following skills: {', '.join(agent['skills'])}."
    if "goals" in agent:
        system_instructions += f"\nYour goals are: {', '.join(agent['goals'])}."
    #******************************************************    
    
    
    
    # Example usage:
    strings = agent.get("tools") #["get_current_weather", "write_script"]
    object_names = strings_to_object_names(strings)
    #print("strings from agent is --",strings)
    # #print("object names from agent is --",object_names)

    tools = []
    for object_name in object_names:
        try:
            tool = globals()[object_name]
            tools.append(tool)
        except KeyError:
            print(f"Object '{object_name}' not found.")
        
        
        #print()  # Print an empty line
        #print("The tool object = +++++++++++++++++++++",tools) 
        #print()  # Print an empty line   
        

    #******************************************************    
    response = openai_api(system_instructions, user_query, context_data, tools)
    return response

def main():
    
    agent_files = ["agent1.json", "agent2.json", "agent3.json", "agent4.json"]
    user_query = "wrie one interesting fact about cropcircles?"
    context_data = {"topic": "cropcircles", "date": "October 26, 2023"}

    for agent_file in agent_files:
        print(f"\n--- Running Agent: {agent_file} ---")
        
        
        if agent_file == "agent1.json":
            user_query = "write one line interesting facts about the oceans? simple answer"
            context_data = {"topic": "colour of the ocean", "date": "October 26, 2023"}
            
            
        elif agent_file == "agent2.json":
            user_query = "what is the cycle of the moon in days? simple answer"
            context_data = {"topic": "raindropplets", "date": "October 26, 2023"}
            
        elif agent_file == "agent3.json":
            user_query = "one sentence about, What are doctors looking for? simple answer"
            context_data = {"topic": "cropcircles", "date": "October 26, 2023"}
            
        elif agent_file == "agent4.json":
            user_query = "write a script about london and a bad storm, use {write_script} tool AS THE FOCUS to generate the script"   
            context_data = {"topic": "plan a trip", "date": "October 26, 2025"}
            
        
        
        
        response = run_agent(agent_file, user_query, context_data)
        if response:
            print()  # Print an empty line
            print("Agents reponse ",response)
            print()  # Print an empty line
        else:
            print("Agent execution failed.")



if __name__ == "__main__":
        # Create sample agent JSON files if they don't exist
        if not os.path.exists("agent1.json"):
            with open("agent1.json", "w") as f:
                json.dump({"name": "CosmosExplorer", "role": "An expert in cosmology.", "skills": ["Explaining complex astronomical concepts", "Summarizing scientific papers"], "goals": ["To educate users about the universe."], "tools": []}, f, indent=4)
        if not os.path.exists("agent2.json"):
            with open("agent2.json", "w") as f:
                json.dump({"name": "FactFinder", "role": "A meticulous researcher.", "skills": ["Fact-checking", "Information retrieval"], "goals": ["To provide accurate and verifiable information."], "tools": []}, f, indent=4)
        if not os.path.exists("agent3.json"):
            with open("agent3.json", "w") as f:
                json.dump({"name": "CreativeWriter", "role": "A creative writer specializing in science fiction.", "skills": ["Storytelling", "World-building"], "goals": ["To create engaging and imaginative narratives."], "tools": []}, f, indent=4)
        if not os.path.exists("agent4.json"):
            with open("agent4.json", "w") as f:
                json.dump({"name": "DataAnalyst", "role": "A data analyst with a focus on scientific data.", "skills": ["Statistical analysis", "Data visualization"], "goals": ["To identify patterns and trends in scientific data."], "tools": []}, f, indent=4)

main()