import asyncio
from agents import AGENTS, ask_agent, make_consensus

async def run_debate(
    question: str,
    context: list = None,
    progress_callback=None
) -> dict:
    answers = {}

    async def query(name):
        loop   = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None, ask_agent, name, question, context
        )
        answers[name] = answer
        if progress_callback:
            await progress_callback(name, answer)

    await asyncio.gather(*[query(name) for name in AGENTS])

    loop      = asyncio.get_event_loop()
    consensus = await loop.run_in_executor(
        None, make_consensus, question, answers, context
    )

    return {"answers": answers, "consensus": consensus}
