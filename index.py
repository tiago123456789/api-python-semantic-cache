import os
from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize import OpenAITextVectorizer
from openai import OpenAI
from fastapi_openai_compat import CompletionResult, MessageParam, create_chat_completion_router
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()

vectorizer = OpenAITextVectorizer(
    model="text-embedding-3-small",
)

cache = SemanticCache(
    redis_url=os.getenv("REDIS_URI"),
    distance_threshold=os.getenv("DISTANCE_SEMANTIC_CACHE"),
    vectorizer=vectorizer,
    overwrite=True,
    ttl=int(os.getenv("CACHE_TTL"))
)


app = FastAPI()

def list_models() -> list[str]:
    models = client.models.list()
    model_ids: list[str] = []
    for model in models:
        model_ids.append(model.id)

    return model_ids

async def run_completion(model: str, messages: list[MessageParam], body: dict) -> CompletionResult:
    lastUserMessage: str
    for message in messages:  
        if (message.get("role") == "user"):
            lastUserMessage = message.get("content")

    cached_response = cache.check(
        prompt=lastUserMessage
    ) 

    if cached_response:
        print("Found in cache!!!")
        return cached_response[0].get("response")

    result = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    answer = result.choices[0].message.content
    cache.store(
        prompt=lastUserMessage, 
        response=answer,  
    )
    
    return answer


app = FastAPI()

@app.middleware("http")
async def has_authorization(request: Request, call_next):
    api_key = (request.headers.get("x-api-key"))

    if api_key == None:
        return JSONResponse(
            content={ "message": "You need to provide the api key via header 'x-api-key'" },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    
    apiKeyAuthorizated = os.getenv("API_KEY")
    if api_key != apiKeyAuthorizated:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={ "message": "You do not have permission to access the resource" }
        )


    response = await call_next(request)
    return response


router = create_chat_completion_router(
    list_models=list_models,
    run_completion=run_completion,
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
