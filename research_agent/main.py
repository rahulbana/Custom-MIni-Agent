import asyncio
from datetime import datetime
from loguru import logger
from research_agent.agent import ResearchAgent
from research_agent.config import LOGS_DIR, OUTPUTS_DIR

async def main(query):
    # Setup logging to file inside logs/
    log_path = LOGS_DIR / "research_agent.log"
    logger.add(str(log_path), rotation="1 day", level="INFO")
    logger.info("Starting research agent...")
    
    agent = ResearchAgent()
    result = await agent.research(query, depth=2, verify=True)
    
    # Console output
    print("\n" + "="*80)
    print(f"RESEARCH REPORT: {result['topic']}\n")
    print(result["report"])
    print("\n" + "="*80)
    print("SOURCES USED:")
    for url in result["sources"]:
        print(f"  - {url}")
    print("\nSummary:", result["summary"])
    
    # Save report with timestamp inside outputs/
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUTS_DIR / f"research_output_{timestamp}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {result['topic']}\n\n")
        f.write(result["report"])
        f.write("\n\n## References\n")
        for url in result["sources"]:
            f.write(f"- {url}\n")
    
    logger.info(f"Report saved to {output_path}")
    print(f"\n✅ Report saved to {output_path}")

if __name__ == "__main__":
    query = input("Enter your research query: ") #The current state of quantum machine learning algorithms
    asyncio.run(main(query))
