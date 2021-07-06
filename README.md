



## **FORM TELEGRAM BOT**

A *open-source bot* is developed for the purpose of creating and answering forms like Google Forms.

Check out the bot [here](https://telegram.me/form_telebot) 

## **Features :**

 - Users can able to create forms and maintain them
 - Users can share the generated form link to others to get responses
 - Users can able to answer specific form by using the link
 - Users can able to get answers for their forms in `.csv` file 


## **How to use ?**

1. Start the [bot](https://telegram.me/form_telebot)

2. Press **Menu** button to get the options or press Menu (blue) to get available commands

3. You find various menu buttons as given below

4. Select **Create** button to create your own form
    > Enter your form title, no of questions and type the questions one by one

    > Atlast, a link will be generated for the current form which you can share to others and get their response
5. Select **View** button to view your forms
    > It shows all the titles and select the desired form by tapping the corresponding number below

    > It provides the form details and share button for selecting the contact to share

6. Select **Answers** button to get answers for your forms
    > It shows all the titles and select the desired form by tapping the corresponding number below
    
    >It provides preview and .csv file for the answers of the selected form
    
7.  Select **Help** button to show the available commands
8.  Select **Bot Stats** to get current bot statistics 

## **How to deploy ?**
	
Developers either use *heruko like online server* or make their computer as server for deploying this bot by :
	
1.  Ensure you have `python3` installed 

2. Clone this repository to your machine

3. Create a virtual python environment by `python3 -m venv project` and activate it

4. Install the required libraries by `pip install -r requirements.txt`

5.  Now, go to @BotFather in telegram, create a new bot and get the bot token

6. Enter the bot token and your username in `CONFIG.py` 

7.   Run `python3 main.py`
	

