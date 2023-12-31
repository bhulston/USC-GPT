---
license: apache-2.0
title: USC-GPT
sdk: streamlit
emoji: 📚
colorFrom: pink
colorTo: yellow
pinned: true
---
# USC-GPT
A simple MVP chatbot that uses a pinecone vector database of USC Spring 2024 classes and OpenAI's GPT to help students find classes! Using RAG and Prompt Engineering
Will update this with a space to include your own OpenAI API/use a free LLM if people start using it a lot, for now I am using my own account. (So don't spam plz<3)

![image/png](https://cdn-uploads.huggingface.co/production/uploads/63cc674af488db9bb3ca3bd5/c5ySQCW9C2rIq1Rol-Pp2.png)

Starting with the USC schedule of classes website for all classes provided, and following that stored and embedded them into a vector database (Pinecone!).
Then using multiple agents to handle different steps in the process (to abstract away prompt engineering from the user to the backend), we are able to do complex searches to help students find their ideal class:)

## Room for Improvement:
1. Using fine-tuned BERT models for certain agents (Using an LLM is easier, but a bit overkill in this scenario)
2. Optimizing RAG searches and incorporating more information about classes in GPT responses
3. Support for a user to choose what language models to use

## Agents
We use agents as a simple and easy way to handle some complex NLP tasks. These could likely be handled in other ways.
#### Filter Agent:
An agent to extract filters from the user's query and removing them from the query used in searching the vector DB.

#### Keywords Agent:
Extracting keywords from the query. In order to optimize the vector DB search, I have found that combining a user's original query with some keywords related to the class they are using helps in optimizing the vector search.

#### Results Agent:
This agent processes the similarity searches from the vector database to output it in a user friendly manner. There is also some judgement given to this in interpreting what class is recommended to a user.


## Example of Agents in Action
Here's an example I've already built:):

#### Original Query:
"I want to take a Video game class, with 3-D modeling on Tuesdays and Thursdays before 5 pm"

#### Result Agent Response:
```
Based on the scores and course content, I would recommend "ITP 351: 3D Character Modeling for Games" as it specifically focuses on 3D modeling for games and has a lower score of 0.856241643. 
However, if you'd rather a course with more focus on the foundations of 3D gaming, "CTIN 583: Game Development for Designers" represents a good choice and has the lowest score of 0.845549047. 
Please bear in mind that the courses may have prerequisites. If you have taken any prerequisites in past semesters, you should be eligible for either course. 
Otherwise, the introductory course "ITP 215L: Introduction to 3D Modeling, Animation, and Visual Effects" could serve as a starting point.
```