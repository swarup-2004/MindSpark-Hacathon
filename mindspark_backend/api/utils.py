from transformers import pipeline
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
from django.http import HttpResponse

import matplotlib
matplotlib.use('Agg') 


def generate_summary(full_content):
    # Initialize the summarization pipeline
    summarizer = pipeline("summarization")

    # Set the max input length for the summarization model
    max_input_length = 1024  # Adjust this based on your model's capabilities
    chunks = []

    # Split the content into chunks if it's too long
    if len(full_content) > max_input_length:
        chunks = [full_content[i:i + max_input_length] for i in range(0, len(full_content), max_input_length)]
    else:
        chunks = [full_content]

    # Summarize each chunk and collect the results
    summary = []
    for chunk in chunks:
        summary_chunk = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary.append(summary_chunk[0]['summary_text'])

    # Combine summaries into a final summary
    final_summary = ' '.join(summary)
    return final_summary

def analyze_sentiment(full_content):
    # Initialize the sentiment-analysis pipeline
    sentiment_analyzer = pipeline("sentiment-analysis")

    
    # Split the content into manageable chunks
    max_input_length = 512
    chunks = [full_content[i:i + max_input_length] for i in range(0, len(full_content), max_input_length)]
    
    # Analyze sentiment for each chunk
    results = []
    for chunk in chunks:
        sentiment_result = sentiment_analyzer(chunk)
        results.extend(sentiment_result)
    
    # Combine results (you may want to aggregate or just return the results)
    return results


def generate_word_cloud(article):
    # Get the full content of the article
    full_content = article.full_content

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(full_content)

    # Create a BytesIO buffer to save the image
    buffer = io.BytesIO()

    # Plot the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Turn off axis numbers and ticks

    # Save the figure to the buffer
    plt.savefig(buffer, format='png')
    plt.close()  # Close the figure to avoid display in Jupyter notebook

    # Move the buffer cursor to the beginning
    buffer.seek(0)

    # Create an HTTP response with the image
    return HttpResponse(buffer.getvalue(), content_type='image/png')







# Function to classify news articles as Fake or Not Fake
def classify_news_articles_fake_or_not(full_content):
    # Assume you have a generate_summary function that summarizes the content
    # full_content = generate_summary(full_content)

    fake_news_classifier = pipeline("text-classification", model="vikram71198/distilroberta-base-finetuned-fake-news-detection")
    
    # Map labels
    label_mapping = {
        "LABEL_0": "Not Fake News",
        "LABEL_1": "Fake News"
    }

    # Split the content into manageable chunks
    max_input_length = 512
    chunks = [full_content[i:i + max_input_length] for i in range(0, len(full_content), max_input_length)]
    
    # Analyze fake news detection for each chunk
    results = []
    for chunk in chunks:
        result = fake_news_classifier(chunk)
        results.extend(result)  # Append the result to the results list
    
    # Initialize counters
    fake = 0
    fake_score = 0
    not_fake = 0
    not_fake_score = 0

    # Debugging output
    # print(results)

    # Process results
    if results:
        for val in results:
            # Check the label and update counters
            if val['label'] == "LABEL_0":
                not_fake += 1
                not_fake_score += val['score']
            else:
                fake += 1
                fake_score += val['score']

    # Debugging output for counters
    # print(fake, fake_score, not_fake, not_fake_score)
    
    # Determine if content is fake or not based on the results
    if fake > not_fake and fake != 0:
        return {"Fake News": float(fake_score) / fake}
    elif not_fake != 0:
        return {"Not Fake News": float(not_fake_score) / not_fake}
    else:
        return {"Not Fake News": 98.5}  # Default case

