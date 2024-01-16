from fastapi import FastAPI, Query
from database.mongo import DatabaseClient  # Adjust the import path as needed
from utils.types import TokenCounts
from typing import List
from metrics.aggregate import aggregate_throughputs, aggregate_ttft
from providers.provider_factory import ProviderFactory
from utils.types import ModelName
from database.models.metrics import get_static_data

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await DatabaseClient.connect()
    await DatabaseClient.create_indexes()
    print("connected to databases")


@app.on_event("shutdown")
async def shutdown_event():
    await DatabaseClient.disconnect()


@app.get("/")
def root():
    return {"message": "Provider Leaderboard is up and running!"}


@app.get("/get-provider-data")
async def get_provider_data(
    output_tokens: TokenCounts = Query(...),
    num_concurrent_request: int = Query(...),
    selected_models: List[str] = Query(...),
    num_days: int = Query(5),
):
    model_names = []
    if "llama2-70b-chat" in selected_models:
        model_names.append("llama2-70b-chat")
    if "mixtral-8x7b" in selected_models:
        model_names.append("mixtral-8x7b")
    if "OpenAI models" in selected_models:
        model_names.append(
            ModelName.GPT4.value, ModelName.GPT4_TURBO.value, ModelName.GPT3_TURBO.value
        )
    if "Anthropic models" in selected_models:
        model_names.append(ModelName.CLAUDE2.value, ModelName.CLAUDE_INSTANT.value)

    data = []
    for provider_name in ProviderFactory.get_all_provider_names():
        for model in model_names:
            throughput = await aggregate_throughputs(
                provider_name, model, output_tokens, num_concurrent_request, num_days
            )
            ttft = await aggregate_ttft(
                provider_name, model, num_concurrent_request, num_days
            )
            if not throughput or not ttft:
                continue
            static_data = await get_static_data(provider_name)
            provider_stats = {
                "provider": provider_name,
                "url": static_data.get("url"),
                "logo_url": static_data.get("logo_url"),
                "model": model,
                "cost": static_data.get("cost")[model],
                "rate_limit": static_data.get("rate_limit"),
                "throughput": throughput,
                "ttft": ttft,
            }
            data.append(provider_stats)
    return data
