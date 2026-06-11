import json
import random
import uuid

MENUS = {
    "Home": "  1. Recipes — navigate to Recipes tools\n  2. Meal Plan — navigate to Meal Plan tools\n  3. Groceries — navigate to Groceries tools\n  4. Pantry — navigate to Pantry tools\n  5. Nutrition — navigate to Nutrition tools\n  6. Dietary — navigate to Dietary tools\n  7. Favorites — navigate to Favorites tools\n  8. MEM [note: `string`] — store a memory note (10–20 words exactly)\n  9. BACK — go to previous state\n  10. DONE — task is complete",
    "Recipes": "  1. add_recipe [name: `string`, steps: `multiline_string`]\n  2. search_recipes [ingredient: `string`]\n  3. scale_recipe [id: `int`, servings: `int`]\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE",
    "Meal Plan": "  1. add_to_plan [recipe_id: `int`, day: `string`, meal: `string`]\n  2. clear_day_plan [day: `string`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
    "Groceries": "  1. generate_shopping_list [start_date: `date`, end_date: `date`]\n  2. mark_item_bought [item: `string`]\n  3. add_custom_grocery [item: `string`]\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE",
    "Pantry": "  1. add_to_pantry [item: `string`, qty: `int`]\n  2. remove_from_pantry [item: `string`]\n  3. check_expirations\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE",
    "Nutrition": "  1. get_recipe_macros [recipe_id: `int`]\n  2. get_daily_macros [day: `string`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
    "Dietary": "  1. set_allergies [allergies: `list`]\n  2. filter_recipes_by_diet [diet: `string`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
    "Favorites": "  1. favorite_recipe [id: `int`]\n  2. list_favorites\n  3. rate_recipe [id: `int`, stars: `int`]\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE"
}

ACTION_MAP = {
    "Home": {"Recipes": 1, "Meal Plan": 2, "Groceries": 3, "Pantry": 4, "Nutrition": 5, "Dietary": 6, "Favorites": 7, "MEM": 8, "BACK": 9, "DONE": 10},
    "Recipes": {"add_recipe": 1, "search_recipes": 2, "scale_recipe": 3, "MEM": 4, "BACK": 5, "DONE": 6},
    "Meal Plan": {"add_to_plan": 1, "clear_day_plan": 2, "MEM": 3, "BACK": 4, "DONE": 5},
    "Groceries": {"generate_shopping_list": 1, "mark_item_bought": 2, "add_custom_grocery": 3, "MEM": 4, "BACK": 5, "DONE": 6},
    "Pantry": {"add_to_pantry": 1, "remove_from_pantry": 2, "check_expirations": 3, "MEM": 4, "BACK": 5, "DONE": 6},
    "Nutrition": {"get_recipe_macros": 1, "get_daily_macros": 2, "MEM": 3, "BACK": 4, "DONE": 5},
    "Dietary": {"set_allergies": 1, "filter_recipes_by_diet": 2, "MEM": 3, "BACK": 4, "DONE": 5},
    "Favorites": {"favorite_recipe": 1, "list_favorites": 2, "rate_recipe": 3, "MEM": 4, "BACK": 5, "DONE": 6}
}

def generate_trace(task, steps):
    turns = []
    state_stack = ["Home"]
    current_memory = None
    last_result = None

    for step in steps:
        target_action_str, args_dict, expected_result, reason = step
        current_state = state_stack[-1]

        action_id = ACTION_MAP[current_state][target_action_str]

        # Build USER prompt
        user_prompt = f"[TASK]: {task}\n[STATE]: {current_state}"
        if current_memory:
            user_prompt += f"\n[MEMORY]: {current_memory}"
        if last_result is not None:
            user_prompt += f"\n[RESULT]: {last_result}"
        user_prompt += f"\n[MENU]:\n{MENUS[current_state]}"

        # Build ASSISTANT response
        ast_response = {
            "reason": reason,
            "action": action_id
        }
        if args_dict is not None and len(args_dict) > 0:
            ast_response["args"] = args_dict

        if target_action_str == "MEM":
            words = args_dict["note"].split()
            if not (10 <= len(words) <= 20):
                raise ValueError(f"MEM note must be 10-20 words. Got {len(words)}: '{args_dict['note']}'")
            current_memory = args_dict["note"]

        turns.append({
            "user": user_prompt,
            "assistant": json.dumps(ast_response)
        })

        if current_state == "Home" and target_action_str in ["Recipes", "Meal Plan", "Groceries", "Pantry", "Nutrition", "Dietary", "Favorites"]:
            state_stack.append(target_action_str)
            last_result = None
        elif target_action_str == "BACK":
            state_stack.pop()
            last_result = None
        elif target_action_str == "DONE":
            break
        elif target_action_str == "MEM":
            last_result = None
        else:
            last_result = expected_result

    return {
        "task": task,
        "turns": turns
    }

traces = []

# Theme 1: "Web research then save result" mapped to "Search recipes then add custom grocery" (10 traces)
for i in range(10):
    item = ["apples", "beef", "carrots", "dates", "eggplant", "figs", "garlic", "honey", "iceberg lettuce", "jalapenos"][i]
    task = f"Find a recipe with {item} and then add that key ingredient to my grocery list manually."
    steps = [
        ("Recipes", {}, None, f"I need to search for recipes containing {item}. I will start by navigating to the Recipes domain from the Home menu."),
        ("search_recipes", {"ingredient": item}, f"1. {item.title()} Salad (ID: 10{i})\n2. Baked {item.title()} (ID: 20{i})", f"Now that I am in the Recipes domain, I will use the search tool. This will help me find dishes that prominently feature {item} as requested."),
        ("MEM", {"note": f"Searched for {item} recipes and found good options, now I must add it to groceries."}, None, f"I will save a quick note to remember that I need to add {item} to the groceries. It is important to keep track of this next step."),
        ("BACK", {}, None, "Now that I have verified the ingredient exists in recipes, I need to go back. I will return to the Home menu to access other domains."),
        ("Groceries", {}, None, "From the Home menu, I will navigate to the Groceries domain. This is where I can add the ingredient manually to the list."),
        ("add_custom_grocery", {"item": item}, f"Added {item} to your grocery list.", f"I am adding {item} to the custom grocery list. This fulfills the second part of the user task successfully."),
        ("DONE", {}, None, "Both tasks are complete. I have searched for the recipe and added the item to groceries. There is nothing left to do here.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 2: "Email reading and calendar scheduling" mapped to "Check expirations and add to meal plan" (8 traces)
for i in range(8):
    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Next Monday"][i]
    task = f"Check what is expiring soon in the pantry and schedule a meal for {day} to use it up."
    steps = [
        ("Pantry", {}, None, "I first need to see what is expiring in the pantry. To do this, I will navigate to the Pantry domain."),
        ("check_expirations", {}, f"Expiring soon:\n- Milk (2 days)\n- Tofu (3 days)", "I am checking the expiration dates now. This will tell me which ingredients need to be consumed immediately."),
        ("MEM", {"note": f"Checked expirations and saw that Milk and Tofu are expiring soon. Will schedule for {day}."}, None, "I will record the expiring items in memory. This ensures I can use them when planning the upcoming meal later."),
        ("BACK", {}, None, "I have the expiration info from the pantry. Therefore, I need to go back to the Home menu now."),
        ("Meal Plan", {}, None, "I will navigate to the Meal Plan domain next. This will allow me to schedule a meal using the expiring items."),
        ("add_to_plan", {"recipe_id": 42 + i, "day": day, "meal": "Dinner"}, f"Recipe {42+i} scheduled for {day} Dinner.", f"I am scheduling a suitable recipe for {day} dinner. This meal effectively uses the expiring pantry ingredients we checked earlier."),
        ("DONE", {}, None, "The pantry check is complete and the meal has been scheduled successfully to use the items. This completes all parts of the user request.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 3: "Write and run Python code, handle an error, fix and rerun" mapped to "Error handling: Invalid ID when getting macros" (8 traces)
for i in range(8):
    task = f"Get the nutritional macros for the 'Chicken Alfredo' recipe. I think its ID is {900+i}."
    steps = [
        ("Nutrition", {}, None, "I need to fetch the recipe macros based on the provided ID. I will go to the Nutrition domain first to access the macro tools."),
        ("get_recipe_macros", {"recipe_id": 900 + i}, "Error: Recipe ID not found in the database.", f"I am trying to get the nutritional info using the provided ID {900+i}. This will show me the macros for the specified recipe."),
        ("BACK", {}, None, "Since the ID was wrong, I have to go back to the Home menu. From there, I can access the Recipes domain to search."),
        ("Recipes", {}, None, "I am entering the Recipes domain now. This will allow me to search for the correct 'Chicken Alfredo' recipe ID."),
        ("search_recipes", {"ingredient": "Chicken Alfredo"}, "1. Chicken Alfredo Classic (ID: 55)\n2. Keto Alfredo (ID: 56)", "I am searching for the dish by name. This will help me find its actual recipe ID in the system database."),
        ("BACK", {}, None, "I found the correct ID is 55. I will go back to the Home menu so I can return to the Nutrition domain."),
        ("Nutrition", {}, None, "Now I will enter the Nutrition domain again. This time I have the correct recipe ID in hand to get the macros."),
        ("get_recipe_macros", {"recipe_id": 55}, "Calories: 850, Protein: 45g, Carbs: 60g, Fat: 40g", "I will request the macros again. This time I am using the verified recipe ID 55 from my earlier search."),
        ("DONE", {}, None, "I have successfully retrieved the required macros after fixing the incorrect ID issue. The task is now complete.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 4: "Load or compute data, plot or calculate" mapped to "Get daily macros and scale recipe" (8 traces)
for i in range(8):
    task = f"Check my total daily macros for today and then scale up recipe {100+i} to 6 servings."
    steps = [
        ("Nutrition", {}, None, "I need to check today's daily macros first. I will navigate to the Nutrition domain to find the appropriate tool."),
        ("get_daily_macros", {"day": "today"}, "Today's Macros - Calories: 1500, Protein: 90g, Fat: 50g, Carbs: 180g", "I am retrieving the daily macro summary. This will fulfill the first part of the user's request regarding today's totals."),
        ("MEM", {"note": f"Retrieved daily macros showing 1500 calories today. Now I need to scale recipe {100+i} up."}, None, "I will store the successful macro retrieval in memory. This ensures I remember to move on to scaling the recipe next."),
        ("BACK", {}, None, "The daily macros are confirmed and noted. I am going back to the Home menu now to switch domains."),
        ("Recipes", {}, None, "I need to scale a recipe now. This requires navigating into the Recipes domain from the Home menu."),
        ("scale_recipe", {"id": 100 + i, "servings": 6}, f"Recipe {100+i} scaled to 6 servings successfully.", "I am using the scale tool to adjust the serving size. This scales the specified recipe to 6 servings as requested."),
        ("DONE", {}, None, "I have checked the daily macros and scaled the recipe appropriately. This completes all steps of the assigned task.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 5: "Multi-domain" mapped to "Dietary + Favorites" (10 traces)
for i in range(10):
    diet = ["vegan", "keto", "paleo", "vegetarian", "gluten-free", "pescatarian", "low-carb", "dairy-free", "nut-free", "whole30"][i]
    task = f"Filter recipes by the {diet} diet and add my favorite recipe 77 to my favorites list."
    steps = [
        ("Dietary", {}, None, "I need to filter recipes by dietary preference first. I will enter the Dietary domain to access the filtering tool."),
        ("filter_recipes_by_diet", {"diet": diet}, f"Found 15 {diet} recipes. Top picks: ID 12, ID 19, ID 34.", f"I am filtering the recipe database now. This will help me find suitable options that strictly match the {diet} diet."),
        ("MEM", {"note": f"Successfully filtered recipes for the {diet} diet. Now I must navigate to favorites for recipe 77."}, None, f"I will save a note confirming the {diet} filter worked. This helps me remember to add the favorite recipe item next."),
        ("BACK", {}, None, "Dietary filtering is done and noted. I will go back to the Home menu to access the Favorites domain."),
        ("Favorites", {}, None, "I am entering the Favorites domain now. This is where I can add the specified recipe to the user's saved list."),
        ("favorite_recipe", {"id": 77}, "Recipe 77 has been added to your favorites.", "I am saving recipe 77 to the favorites list. This completes the user's explicit instructions for saving the favorite."),
        ("DONE", {}, None, "Both the dietary filtering and favorite addition are complete. I will finish the task since all requirements are met.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 6: "BACK correction" mapped to "Wrong domain -> BACK -> Correct domain" (8 traces)
for i in range(8):
    task = f"Generate a shopping list for next week, starting 2024-11-{10+i} to 2024-11-{17+i}."
    steps = [
        ("Pantry", {}, None, "I need to generate a shopping list. I think the tools for this might be located in the Pantry domain."),
        ("check_expirations", {}, "Expiring soon: None", "Let me check expirations first. This might help with generating the shopping list directly here in the pantry."),
        ("MEM", {"note": "Checking the pantry was the wrong move for generating a shopping list. I should go back."}, None, "I realize Pantry does not have the shopping list tool. I need to note this mistake so I do not repeat it."),
        ("BACK", {}, None, "I am currently in the wrong domain for this task. I will go back to the Home menu immediately to find the right one."),
        ("Groceries", {}, None, "The Groceries domain is the correct place to generate a shopping list. I am navigating there right now."),
        ("generate_shopping_list", {"start_date": f"2024-11-{10+i}", "end_date": f"2024-11-{17+i}"}, "Shopping list generated with 24 items.", "I am using the correct tool to generate the grocery list. This will cover the requested date range perfectly."),
        ("DONE", {}, None, "The shopping list has been successfully generated in the correct domain. The task is completely finished.")
    ]
    traces.append(generate_trace(task, steps))

# Theme 7: "Short tasks" mapped to "Just mark an item bought" (8 traces)
for i in range(8):
    item = ["milk", "bread", "eggs", "butter", "cheese", "yogurt", "chicken", "rice"][i]
    task = f"I just bought {item}, please mark it as bought."
    steps = [
        ("Groceries", {}, None, f"To mark {item} as bought, I need to navigate straight to the Groceries domain. I will do that from the Home menu."),
        ("mark_item_bought", {"item": item}, f"{item.title()} marked as bought and removed from active list.", f"I am checking off {item} from the shopping list. This updates the list since the user has already purchased it."),
        ("MEM", {"note": f"Successfully marked {item} as bought from the shopping list. Task is completed easily."}, None, "I will save a quick note that the item was purchased. This acts as a confirmation before finishing."),
        ("DONE", {}, None, "The task of marking the grocery item as bought is done. No further actions are needed from me here.")
    ]
    traces.append(generate_trace(task, steps))

# Shuffle to mix themes randomly
random.seed(42)
random.shuffle(traces)

# Save to JSONL
filename = f"dataset_{uuid.uuid4().hex[:8]}.jsonl"
with open(filename, "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")

print(f"Generated {len(traces)} traces in {filename}")
