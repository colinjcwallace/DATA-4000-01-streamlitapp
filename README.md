# Streamlit Food Inventory App

## Student Name
Colin Wallace

## App Description
This app will help users manage their household food inventory. Designed to take inputs for groceries and recipes, this app will allow users to see what they have in their house and what they will need to get to cook their meals. Additionally, this app will show the nutritional value of the food they eat to help those who are trying to diet. This will relieve stress, save time, and help with wasting food unnecessarily. 

Update:

Currently this app logs inventory of user's groceries in a database. Users can now delete items from inventory and will be shown in an output table. User inputs are loaded into the database system, Supabase, using an API key. 

Update:

I have added three seperate pages to organize the app and its functions. The first page selects the stored recipes and gives you the directions as well as what ingredients you will need and what you will need to go to the store for. The second page is your inventory manager, where you add or subtract from your inventory. This page also shows the total of each item in your inventory. The last page is your recipe manager. In this page you add your ingredients, its quantities, and the directions for that recipe. New ingredients get stored in the data dictionary in the database but not in inventory. 

## Intended Users

This app is intended for those who buy groceries and cook for themselves. 

## Current Features

- Feature 1: Selection for stored recipes.

- Feature 2: Output for directions of the recipe.

- Feature 3: Output for ingredients in house and those to buy.

- Feature 4: Ribbon for pages.

- Feature 5: Input for add or subtract items into inventory.

- Feature 6: Output of current inventory as sum of all transactions.

- Feature 7: Output of transaction table.

- Feature 8: Input to create a new recipe.

- Feature 9: Selection box for stored recipes add new ingredients and directions

- Feature 10: Tabs to differentiate adding ingredients and directions

- Feature 11: Input for new ingredients

- Feature 12: Input for new directions

## Planned Features

- Feature 1: Editting feature for ingredients and directions in page 2.

- Feature 2: Need to add quantity to ingredient check in app page

- Feature 3: Add a search to Current Fridge (change name) Contents table in page 1. 

## Ditched Features

- The delete button is no longer a button.

- I will not be doing the dietary aspect yet.

- Shelf life indicator.

## To Do List

- Create more user friendly with inputs. Have not checked errors in user input.

- View transaction history table in page 1 should be a head so millions of entries will not show in long-term use. Or just delete feature as it is not critical.

- Change names of pages

- Make it look nice

## Challenges Faced

- The biggest challenged I faced with this project is how to organize the database. I was doing this while learning how to navigate the features of Supabase. I found it easier to use SQL to create tables, their contingencies, and keys rather than using Supabase's user inputs.