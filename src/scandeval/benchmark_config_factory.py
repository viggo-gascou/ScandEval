"""Factory class for creating dataset configurations."""

import torch

from .config import BenchmarkConfig, DatasetTask, Language
from .dataset_tasks import get_all_dataset_tasks
from .enums import Device, Framework
from .languages import get_all_languages


def build_benchmark_config(
    language: str | list[str],
    model_language: str | list[str] | None,
    dataset_language: str | list[str] | None,
    dataset_task: str | list[str] | None,
    batch_size: int,
    raise_errors: bool,
    cache_dir: str,
    evaluate_train: bool,
    use_auth_token: bool | str,
    openai_api_key: str | None,
    progress_bar: bool,
    save_results: bool,
    verbose: bool,
    framework: Framework | str | None,
    few_shot: bool,
    device: Device | None,
    trust_remote_code: bool = False,
    testing: bool = False,
) -> BenchmarkConfig:
    """Create a benchmark configuration.

    Args:
        language (str or list of str):
            The language codes of the languages to include, both for models and
            datasets. Here 'no' means both Bokmål (nb) and Nynorsk (nn). Set this
            to 'all' if all languages (also non-Scandinavian) should be considered.
        model_language (str, list of str, or None):
            The language codes of the languages to include for models. If specified
            then this overrides the `language` parameter for model languages.
        dataset_language (str, list of str, or None):
            The language codes of the languages to include for datasets. If
            specified then this overrides the `language` parameter for dataset
            languages.
        dataset_task (str, list of str, or None):
            The tasks to include for dataset. If None then datasets will not be
            filtered based on their task.
        batch_size (int):
            The batch size to use.
        raise_errors (bool):
            Whether to raise errore instead of skipping them.
        cache_dir (str):
            Directory to store cached models.
        evaluate_train (bool):
            Whether to evaluate the training set as well.
        use_auth_token (bool or str):
            The authentication token for the Hugging Face Hub. If a boolean value is
            specified then the token will be fetched from the Hugging Face CLI, where
            the user has logged in through `huggingface-cli login`. If a string is
            specified then it will be used as the token.
        openai_api_key (str or None):
            The OpenAI API key to use for authentication. If None, then None will be
            returned.
        progress_bar (bool):
            Whether progress bars should be shown.
        save_results (bool):
            Whether to save the benchmark results to local JSON file.
        verbose (bool):
            Whether to output additional output.
        framework (Framework or None):
            The model framework to use. If None then the framework will be set
            automatically. Only relevant if `model_id` refers to a local model.
        few_shot (bool):
            Whether to use the few-shot version of the benchmark.
        device (Device or None):
            The device to use for running the models. If None then the device will be
            set automatically.
        trust_remote_code (bool):
            Whether to trust remote code when loading models from the Hugging Face
            Hub.
        testing (bool, optional):
            Whether to run the benchmark in testing mode. Defaults to False.
    """
    languages = prepare_languages(language=language)
    model_languages = prepare_model_languages(
        model_language=model_language,
        languages=languages,
    )
    dataset_languages = prepare_dataset_languages(
        dataset_language=dataset_language,
        languages=languages,
    )

    dataset_tasks = prepare_dataset_tasks(dataset_task=dataset_task)

    torch_device = prepare_device(device=device)

    # Build benchmark config and return it
    return BenchmarkConfig(
        model_languages=model_languages,
        dataset_languages=dataset_languages,
        dataset_tasks=dataset_tasks,
        batch_size=batch_size,
        raise_errors=raise_errors,
        cache_dir=cache_dir,
        evaluate_train=evaluate_train,
        use_auth_token=use_auth_token,
        openai_api_key=openai_api_key,
        progress_bar=progress_bar,
        save_results=save_results,
        verbose=verbose,
        framework=framework,
        few_shot=few_shot,
        device=torch_device,
        trust_remote_code=trust_remote_code,
        testing=testing,
    )


def prepare_languages(language: str | list[str]) -> list[str]:
    """Prepare language(s) for benchmarking.

    Args:
        language (str or list of str):
            The language codes of the languages to include, both for models and
            datasets. Here 'no' means both Bokmål (nb) and Nynorsk (nn). Set this
            to 'all' if all languages (also non-Scandinavian) should be considered.

    Returns:
        list of str:
            The prepared languages.
    """
    # Create a dictionary that maps languages to their associated language objects
    language_mapping = get_all_languages()

    # Create the list `languages`
    if "all" in language:
        languages = list(language_mapping.keys())
    elif isinstance(language, str):
        languages = [language]
    else:
        languages = language

    # If `languages` contains 'no' then also include 'nb' and 'nn'. Conversely, if
    # either 'nb' or 'nn' are specified then also include 'no'.
    if "no" in languages:
        languages = list(set(languages) | {"nb", "nn"})
    elif "nb" in languages or "nn" in languages:
        languages = list(set(languages) | {"no"})

    return languages


def prepare_model_languages(
    model_language: str | list[str] | None,
    languages: list[str],
) -> list[Language]:
    """Prepare model language(s) for benchmarking.

    Args:
        model_language (None, str or list of str):
            The language codes of the languages to include for models. If specified
            then this overrides the `language` parameter for model languages.
        languages (list of str):
            The default language codes of the languages to include.

    Returns:
        list of Language objects:
            The prepared model languages.
    """
    # Create a dictionary that maps languages to their associated language objects
    language_mapping = get_all_languages()

    # Create the list `model_languages`
    model_languages_str: list[str]
    if model_language is None:
        model_languages_str = languages
    elif isinstance(model_language, str):
        model_languages_str = [model_language]
    else:
        model_languages_str = model_language

    # Convert the model languages to language objects
    if "all" in model_languages_str:
        model_languages = list(language_mapping.values())
    else:
        model_languages = [
            language_mapping[language] for language in model_languages_str
        ]

    return model_languages


def prepare_dataset_languages(
    dataset_language: str | list[str] | None,
    languages: list[str],
) -> list[Language]:
    """Prepare dataset language(s) for benchmarking.

    Args:
        model_language (None, str or list of str):
            The language codes of the languages to include for datasets. If
            specified then this overrides the `language` parameter for dataset
            languages.
        languages (list of str):
            The default language codes of the languages to include.

    Returns:
        list of Language objects:
            The prepared dataset languages.
    """
    # Create a dictionary that maps languages to their associated language objects
    language_mapping = get_all_languages()

    # Create the list `dataset_languages_str`
    dataset_languages_str: list[str]
    if dataset_language is None:
        dataset_languages_str = languages
    elif isinstance(dataset_language, str):
        dataset_languages_str = [dataset_language]
    else:
        dataset_languages_str = dataset_language

    # Convert the dataset languages to language objects
    if "all" in dataset_languages_str:
        dataset_languages = list(language_mapping.values())
    else:
        dataset_languages = [
            language_mapping[language] for language in dataset_languages_str
        ]

    return dataset_languages


def prepare_dataset_tasks(dataset_task: str | list[str] | None) -> list[DatasetTask]:
    """Prepare dataset task(s) for benchmarking.

    Args:
        dataset_task (str or list of str or None):
            The tasks to include for dataset. If None then datasets will not be
            filtered based on their task.

    Returns:
        list of DatasetTask:
            The prepared dataset tasks.
    """
    # Create a dictionary that maps benchmark tasks to their associated benchmark
    # task objects
    dataset_task_mapping = get_all_dataset_tasks()

    # Create the list of dataset tasks
    if dataset_task is None:
        dataset_tasks = list(dataset_task_mapping.values())
    elif isinstance(dataset_task, str):
        dataset_tasks = [dataset_task_mapping[dataset_task]]
    else:
        dataset_tasks = [dataset_task_mapping[task] for task in dataset_task]

    return dataset_tasks


def prepare_device(device: Device | None) -> torch.device:
    """Prepare device for benchmarking.

    Args:
        device (Device or None):
            The device to use for running the models. If None then the device will be
            set automatically.

    Returns:
        torch.device:
            The prepared device.
    """
    device_mapping = {
        Device.CPU: torch.device("cpu"),
        Device.CUDA: torch.device("cuda"),
        Device.MPS: torch.device("mps"),
    }
    if isinstance(device, Device):
        return device_mapping[device]

    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")
