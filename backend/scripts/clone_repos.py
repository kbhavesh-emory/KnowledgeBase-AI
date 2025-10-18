#!/usr/bin/env python3
"""
GitHub repository cloning script
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from ingest.github import GitHubLoader
from core.rag import RAGSystem
from config.logging import setup_logging

logger = logging.getLogger(__name__)

def clone_and_process_repositories(repo_urls: list, rag_system: RAGSystem):
    """Clone and process GitHub repositories"""
    github_loader = GitHubLoader()
    
    total_documents = 0
    successful_repos = 0
    
    for repo_url in repo_urls:
        try:
            logger.info(f"🔄 Processing repository: {repo_url}")
            
            documents = github_loader.load_repository(repo_url)
            
            if documents:
                added_count = rag_system.add_documents(documents)
                total_documents += added_count
                successful_repos += 1
                logger.info(f"✅ Added {added_count} documents from {repo_url}")
            else:
                logger.warning(f"⚠️ No documents found in {repo_url}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process {repo_url}: {e}")
            continue
    
    # Cleanup
    github_loader.cleanup()
    
    return successful_repos, total_documents

def main():
    parser = argparse.ArgumentParser(description="Clone and process GitHub repositories")
    parser.add_argument("repos", nargs="+", help="GitHub repository URLs")
    parser.add_argument("--branch", default="main", help="Branch to clone")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    try:
        # Initialize systems
        rag_system = RAGSystem()
        
        # Process repositories
        successful_repos, total_documents = clone_and_process_repositories(
            args.repos, rag_system
        )
        
        logger.info(f"🎉 Completed! Processed {successful_repos}/{len(args.repos)} "
                   f"repositories, added {total_documents} documents")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()