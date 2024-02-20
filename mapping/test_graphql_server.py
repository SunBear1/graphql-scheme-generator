import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL

from generated_graphql_queries import GriseraQuery
from generated_graphql_mutations import GriseraMutation

schema = strawberry.Schema(query=GriseraQuery, mutation=GriseraMutation)

graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
