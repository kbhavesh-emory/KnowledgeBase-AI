# backend/config/settings.py
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # =========================
    # API
    # =========================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # =========================
    # GPU / Embedding
    # =========================
    GPU_DEVICE: str = "cuda"          # "cuda" or "cpu"
    EMBEDDING_BATCH_SIZE: int = 32
    TORCH_DTYPE: str = "float16"

    # Sentence-Transformers embedding model
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    NORMALIZE_EMBEDDINGS: bool = True

    # RAG chunking / retrieval
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    RETRIEVE_K: int = 8
    SCORE_THRESHOLD: float = 0.65

    # =========================
    # LLM (Ollama)
    # =========================
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3:latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # =========================
    # Vector Store
    # =========================
    VECTORSTORE_TYPE: str = "faiss"
    VECTORSTORE_PATH: str = "data/vectorstore"

    # =========================
    # Storage
    # =========================
    PIXELTABLE_PATH: str = "data/knowledgebase.db"

    # =========================
    # GitHub Repositories to clone & embed
    # (Used by scripts/sync_repositories.py by default)
    # =========================
    GITHUB_REPOS: List[str] = Field(default_factory=lambda: [
        "https://github.com/digitalslidearchive/digital_slide_archive",
        "https://github.com/DigitalSlideArchive/HistomicsTK",
        "https://github.com/DigitalSlideArchive/ansible-role-vips",
        "https://github.com/DigitalSlideArchive/base_docker_image",
        "https://github.com/DigitalSlideArchive/dsa_girder_webix_base_viewer",
        "https://github.com/DigitalSlideArchive/DSA_Documentation",
        "https://github.com/DigitalSlideArchive/digitalslidearchive.info",
        "https://github.com/DigitalSlideArchive/pylibtiff",
        "https://github.com/DigitalSlideArchive/CNNCellDetection",
        "https://github.com/DigitalSlideArchive/ctk-cli",
        "https://github.com/DigitalSlideArchive/HistomicsUI",
        "https://github.com/DigitalSlideArchive/DSA-WSI-DeID",
        "https://github.com/DigitalSlideArchive/HistomicsStream",
        "https://github.com/DigitalSlideArchive/tifftools",
        "https://github.com/DigitalSlideArchive/annotation-tracker",
        "https://github.com/DigitalSlideArchive/ImageDePHI-Phase-I",
        "https://github.com/DigitalSlideArchive/HTAN",
        "https://github.com/DigitalSlideArchive/HistomicsDetect",
        "https://github.com/DigitalSlideArchive/girder-client-mount",
        "https://github.com/DigitalSlideArchive/ALBench",
        "https://github.com/DigitalSlideArchive/import-tracker",
        "https://github.com/DigitalSlideArchive/large-image-utilities",
        "https://github.com/DigitalSlideArchive/superpixel-classification",
        "https://github.com/DigitalSlideArchive/histoqc-dsa-plugin",
        "https://github.com/DigitalSlideArchive/wsi-superpixel-guided-labeling",
        "https://github.com/DigitalSlideArchive/ImageDePHI",
        "https://github.com/DigitalSlideArchive/large_image_source_isyntax",
        "https://github.com/DigitalSlideArchive/dive-dsa",
        "https://github.com/DigitalSlideArchive/girder_volview",
        "https://github.com/DigitalSlideArchive/histomics_load_testing",
        "https://github.com/DigitalSlideArchive/histomics-tour",
        "https://github.com/DigitalSlideArchive/dsa-run-custom-ai-models",
        "https://github.com/DigitalSlideArchive/girder-clamav",
        "https://github.com/DigitalSlideArchive/histomicstk-extras",
        "https://github.com/DigitalSlideArchive/girder_assetstore",
        "https://github.com/Gutman-Lab/WSVV",
        "https://github.com/Gutman-Lab/PML",
        "https://github.com/Gutman-Lab/bdsa-model-registry",
        "https://github.com/Gutman-Lab/ihc-tissue-detection",
        "https://github.com/Gutman-Lab/DinoV2_hf",
        "https://github.com/Gutman-Lab/WSIA",
        "https://github.com/Gutman-Lab/neurotk",
        "https://github.com/Gutman-Lab/WSU",
        "https://github.com/Gutman-Lab/dsa-helpers",
        "https://github.com/Gutman-Lab/neurotk-react",
        "https://github.com/Gutman-Lab/DSARequests",
        "https://github.com/Gutman-Lab/slicer-cli-example",
        "https://github.com/Gutman-Lab/raygun",
        "https://github.com/Gutman-Lab/dsa-emory-adrc",
        "https://github.com/Gutman-Lab/plaque-detection-yolo12",
        "https://github.com/Gutman-Lab/wsi-tissue-detection",
        "https://github.com/Gutman-Lab/dsa-czi-converter",
        "https://github.com/Gutman-Lab/WSIVDB",
        "https://github.com/Gutman-Lab/emory-path-qc",
        "https://github.com/Gutman-Lab/BlueBird",
        "https://github.com/Gutman-Lab/LargeImageIterator",
        "https://github.com/Gutman-Lab/comparing-tissue-detection-models",
        "https://github.com/Gutman-Lab/DeidTools",
        "https://github.com/Gutman-Lab/bdsa-workflows-slurm",
        "https://github.com/Gutman-Lab/WSIFE",
        "https://github.com/Gutman-Lab/tissue-plate-specimen-qc",
        "https://github.com/Gutman-Lab/WSIQC",
        "https://github.com/Gutman-Lab/PFM",
        "https://github.com/Gutman-Lab/abeta-tissue-compartment-detection",
        "https://github.com/Gutman-Lab/bdsa-workflows",
        "https://github.com/Gutman-Lab/emory-qc-viz",
        "https://github.com/Gutman-Lab/DSA-Annotation-Browser",
        "https://github.com/Gutman-Lab/ADRC-np-survey-2023-private",
        "https://github.com/Gutman-Lab/osd-paperjs-annotation",
        "https://github.com/Gutman-Lab/bdsa",
        "https://github.com/Gutman-Lab/DSA-Tissue-Reg",
        "https://github.com/Gutman-Lab/Positive-Pixel-Count-",
        "https://github.com/Gutman-Lab/nft-detection",
        "https://github.com/Gutman-Lab/triton-inference",
        "https://github.com/Gutman-Lab/DSA-LLM-Docs",
        "https://github.com/Gutman-Lab/yolov8-nft",
        "https://github.com/Gutman-Lab/cell-tracking-application",
        "https://github.com/Gutman-Lab/ppc-slurm",
        "https://github.com/Gutman-Lab/bdsa-readthedocs",
        "https://github.com/Gutman-Lab/yolo-braak-stage",
        "https://github.com/Gutman-Lab/BrainDigitalSlideArchive",
        "https://github.com/Gutman-Lab/tiling-wsis",
        "https://github.com/Gutman-Lab/wsi-schema-frontend",
        "https://github.com/Gutman-Lab/neuropath-foundation-model",
        "https://github.com/Gutman-Lab/BDSA-Schema-Wrangler",
        "https://github.com/Gutman-Lab/abeta-detection-project",
        "https://github.com/Gutman-Lab/ppc-profiler",
        "https://github.com/Gutman-Lab/BrainSec-py",
        "https://github.com/Gutman-Lab/tissue-detection-att-unet",
        "https://github.com/Gutman-Lab/bdsarepochat",
        "https://github.com/Gutman-Lab/levey-project",
        "https://github.com/Gutman-Lab/dsa-slicer-cli-web-tasks",
        "https://github.com/Gutman-Lab/Dash-Plotly-YOLO",
        "https://github.com/Gutman-Lab/DSAClusterExploration",
        "https://github.com/Gutman-Lab/emory-adrc-dsa",
        "https://github.com/Gutman-Lab/arjita-gray-matter-detection",
        "https://github.com/Gutman-Lab/ADRC-np-survey-2023",
    ])

    # =========================
    # File Processing
    # =========================
    MAX_FILE_SIZE_MB: int = 50
    SUPPORTED_EXTENSIONS: List[str] = Field(default_factory=lambda: [
        ".py", ".md", ".txt", ".rst", ".json", ".yaml", ".yml",
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
        ".html", ".htm", ".xml", ".csv", ".js", ".ts", ".java", ".cpp"
    ])

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
