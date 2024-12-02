## Telling Stories with Data Dashboard
#### Jacob Clement

### Inital submission
The final product for my first submission is `price_mileage_6.py`. 

I scraped `state` from craigslist and used ChatGPT to fill in the gaps. I was almost done with the process so I figured I would submit what I have and try to work with the data for Montana to create a final polished product. The code for the scraping is `scripts/scrape_state.py`.

ChatGPT:
dashboard creation:
https://chatgpt.com/share/670db7df-a534-800a-b24e-4a4fed4b777c

dashboard debugging:
https://chatgpt.com/share/670db7df-a534-800a-b24e-4a4fed4b777c

Web Scraping:
https://chatgpt.com/share/670daba1-86f0-800a-9c97-b771790225d8

Here is a static view of my car, I stopped filtering as the sample is small. My goal is to include a version of this dynamic scatterplot in my final dashboard. There is no output file for this portion. It creates a dash app.

![example](assets\my_car.png)

Github Repo:
https://github.com/jacobchrono/telling_stories_dashboard

### Second Submission

I used panel for this portion of the project.

You should use `html\dynamic_scatter_fail.html` for future examples of bad graphs. ChatGPT defended its output but I could not attach the full convertsation due to a pasted image.

![gpt1](assets\gpt1.png)
![gpt2](assets\gpt2.png)

My vision is to add a widget here the user can build a custom regression model of the full data. I had to limit the number of filters for file size and ability to share so my idea my not be within the scope of the project. Can we share a hosted version over the message board? The final product for this submission is `html\vehicle_dashboard.html`. The relevant python script is `scripts\combine_montana_4.py`.

https://chatgpt.com/share/670ea0a5-5724-800a-8e8f-397db08135d9

### Third Submission

For this submission, I created a streamlit app. Please note that this must be run from the command line. The script is at `final_dash.py`. It is also deployed to the streamlit community cloud 