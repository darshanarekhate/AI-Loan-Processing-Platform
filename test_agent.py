from langchain_core.messages import HumanMessage

from langchain_app.agent import agent


response = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is my loan status?"
            )
        ]
    }
)

print(response["messages"][-1].content)