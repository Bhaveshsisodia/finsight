from graph.state import StockAnalysisState
from graph.nodes import (
    fundamental_node,
    technical_node,
      news_node, fii_dii_node,
        relative_strength_node, probability_node)

try:
    from IPython.display import Image, display
except ImportError:
    Image = display = None



from langgraph.graph import StateGraph , START , END

graph = StateGraph(StockAnalysisState)

graph.add_node('fundamental_node', fundamental_node)
graph.add_node('technical_node', technical_node)
graph.add_node('news_node', news_node)
graph.add_node('fii_dii_node', fii_dii_node)
graph.add_node('relative_strength_node', relative_strength_node)
graph.add_node('probability_node', probability_node)


graph.add_edge(START, 'fundamental_node')
graph.add_edge(START, 'technical_node')
graph.add_edge(START, 'news_node')
graph.add_edge(START, 'fii_dii_node')
graph.add_edge(START, 'relative_strength_node')
graph.add_edge("fundamental_node", 'probability_node')
graph.add_edge("technical_node", 'probability_node')
graph.add_edge("news_node", 'probability_node')
graph.add_edge("fii_dii_node", 'probability_node')
graph.add_edge("relative_strength_node", 'probability_node')
graph.add_edge('probability_node', END)



app=graph.compile()

if __name__ == "__main__":
    # Only run in notebook / direct execution — not during Streamlit import
    if display and Image:
        display(Image(app.get_graph().draw_mermaid_png()))
    with open("graph/workflow_graph.png", "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print("Graph saved to graph/workflow_graph.png")


# result = app.invoke({"symbol": "TORNTPHARM"})