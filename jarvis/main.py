import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import os
import requests
import psutil
import pyjokes
import webbrowser
import platform
import time
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='jarvis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    print("Text-to-speech engine initialized successfully")
except Exception as e:
    print(f"Error initializing text-to-speech engine: {e}")

def speak(text):
    """Convert text to speech"""
    try:
        print(f"Jarvis: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

def take_command():
    """Take voice command from user"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            r.adjust_for_ambient_noise(source, duration=1)
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
        return query.lower()
    except sr.WaitTimeoutError:
        print("No speech detected within the timeout period")
        return "none"
    except sr.UnknownValueError:
        print("Could not understand audio")
        return "none"
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return "none"
    except Exception as e:
        print(f"Error in take_command: {e}")
        return "none"

def get_ai_response(prompt):
    """Get AI-generated response using OpenAI's GPT model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting AI response: {str(e)}")
        return "I'm having trouble processing that right now."

def process_command(command):
    """Process natural language commands."""
    try:
        command = command.lower()
        
        # Handle specific commands
        if 'time' in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {current_time}")
            return
        elif 'date' in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today's date is {current_date}")
            return
        elif 'joke' in command:
            try:
                joke = pyjokes.get_joke()
                speak(joke)
            except Exception as e:
                speak("Sorry, I couldn't find a joke right now.")
            return
        elif 'wikipedia' in command or 'search' in command:
            try:
                search_query = command.replace('wikipedia', '').replace('search', '').strip()
                if not search_query:
                    speak("What would you like to search for?")
                    search_query = take_command()
                    if search_query == "none":
                        return
                
                speak(f'Searching Wikipedia for {search_query}...')
                results = wikipedia.summary(search_query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("There are multiple matches. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find any information about that on Wikipedia.")
            except Exception as e:
                speak("Sorry, I encountered an error while searching Wikipedia.")
            return
        elif 'open website' in command or 'open' in command:
            try:
                website = command.replace('open website', '').replace('open', '').strip()
                # Remove any existing protocol
                website = website.replace('http://', '').replace('https://', '')
                # Add www if not present and not a subdomain
                if not website.startswith('www.') and '.' in website and not any(website.startswith(prefix) for prefix in ['mail.', 'docs.', 'drive.', 'maps.']):
                    website = 'www.' + website
                # Add https protocol
                website = 'https://' + website
                webbrowser.open(website)
                speak(f"Opening {website}")
            except Exception as e:
                logging.error(f"Error opening website: {str(e)}")
                speak("Sorry, I couldn't open the website.")
            return
        elif 'system info' in command or 'system' in command:
            try:
                cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                system = platform.system()
                machine = platform.machine()
                processor = platform.processor()
                
                speak("System Information:")
                speak(f"Operating System: {system}")
                speak(f"Machine Type: {machine}")
                speak(f"Processor: {processor}")
                speak(f"CPU Usage: {cpu_usage}%")
                speak(f"Memory Usage: {memory_usage}%")
            except Exception as e:
                speak("Sorry, I couldn't retrieve system information.")
            return
        elif 'help' in command:
            help_text = """
            I can help you with the following:
            - Tell you the current time
            - Tell you today's date
            - Tell you a joke
            - Search Wikipedia
            - Open websites
            - Show system information
            - Answer general questions
            Just say 'exit' or 'goodbye' when you want to end the conversation.
            """
            speak(help_text)
            return
        
        # For other commands, use OpenAI
        try:
            response = get_ai_response(command)
            speak(response)
        except Exception as e:
            logging.error(f"Error getting AI response: {str(e)}")
            speak("I'm having trouble processing that right now. Please try again.")
        
    except Exception as e:
        logging.error(f"Error processing command: {str(e)}")
        speak("I encountered an error processing your request.")

def wish_me():
    """Greet the user based on time"""
    try:
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            speak("Good Morning!")
        elif 12 <= hour < 18:
            speak("Good Afternoon!")
        else:
            speak("Good Evening!")
        speak("I am Jarvis. How can I help you?")
    except Exception as e:
        print(f"Error in wish_me: {e}")

def main():
    print("Starting Jarvis...")
    
    # Test microphone
    try:
        with sr.Microphone() as source:
            print("Testing microphone...")
            sr.Recognizer().adjust_for_ambient_noise(source, duration=1)
            print("Microphone test successful")
    except Exception as e:
        print(f"Microphone error: {str(e)}")
        print("Please check your microphone connection and permissions")
        return
    
    wish_me()
    
    while True:
        try:
            command = take_command()
            if command and command != "none":
                logging.info(f"User command: {command}")
                
                # Exit command
                if any(word in command for word in ['exit', 'quit', 'bye', 'goodbye']):
                    speak("Goodbye! Have a great day!")
                    break
                
                # Process the command
                process_command(command)
                
        except KeyboardInterrupt:
            print("\nExiting Jarvis...")
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            logging.error(f"Error in main loop: {str(e)}")
            speak("I encountered an error. Please try again.")

if __name__ == "__main__":
    main() 