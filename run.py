from app import app

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

#This file uses Flask boilerplate code.
#Threaded is added so that the application can support multithreading, satisfying scalability requirements.

#NOTE: After running pip install openai, you may find that when pressing "submit" on the answer quesitons page, an error occurs.
#running "#pip install openai==0.28" in CMD may be required to use GradePilot's version, solving the problem.