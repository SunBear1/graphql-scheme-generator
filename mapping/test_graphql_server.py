import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL

from generated_graphql_queries import GriseraQuery

schema = strawberry.Schema(query=GriseraQuery)

graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
