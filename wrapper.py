import requests
import os
import time

class Evo2API:
    """Wrapper for Nvidia's Evo2 Hosted API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://health.api.nvidia.com/v1/biology/arc/evo2-40b"
        
        if not self.api_key:
            raise ValueError("API key required. Set NVIDIA_API_KEY env var or pass api_key parameter")
    
    def generate(self, sequence, num_tokens=100, temperature=1.0, top_k=4, 
                 enable_sampled_probs=False, retry_delay=2):
        """
        Generate DNA sequences using Evo2
        
        Args:
            sequence (str): Input DNA sequence (e.g., "ACGT")
            num_tokens (int): Number of tokens to generate
            temperature (float): Sampling temperature (0.0-2.0)
            top_k (int): Top-k sampling parameter
            enable_sampled_probs (bool): Return probability scores
            retry_delay (int): Delay between requests in seconds
        
        Returns:
            dict: Response containing generated sequence
        """
        # Validate temperature
        if not 0.0 <= temperature <= 2.0:
            temperature = max(0.0, min(2.0, temperature))
            print(f"Warning: Temperature clamped to {temperature}")
        
        url = f"{self.base_url}/generate"
        
        payload = {
            "sequence": sequence,
            "num_tokens": num_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "enable_sampled_probs": enable_sampled_probs
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Add delay to respect rate limits
            time.sleep(retry_delay)
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                error_msg = f"Validation error: {e.response.text}"
                print(f"Error: {error_msg}")
                return None
            elif e.response.status_code == 429:
                print("Rate limit exceeded. Please wait before retrying.")
                return None
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


def main():
    """Example usage"""
    
    # Initialize API (reads from NVIDIA_API_KEY env var)
    api = Evo2API()
    
    print("="*70)
    print("Evo2 DNA Sequence Generation Examples")
    print("="*70)
    
    # Example 1: Simple generation
    print("\n[Example 1] Simple DNA generation")
    print("-" * 70)
    prompt = "ACGT"
    print(f"Prompt: {prompt}")
    
    result = api.generate(sequence=prompt, num_tokens=50)
    if result:
        print(f"Generated: {result['sequence']}")
        print(f"Time: {result['elapsed_ms']}ms")
    
    # Example 2: Longer sequence
    print("\n[Example 2] Longer sequence generation")
    print("-" * 70)
    prompt = "ATGCGATCGATCGATCG"
    print(f"Prompt: {prompt}")
    
    result = api.generate(sequence=prompt, num_tokens=200, temperature=0.8)
    if result:
        print(f"Generated: {result['sequence'][:100]}...")
        print(f"Full length: {len(result['sequence'])} bp")
        print(f"Time: {result['elapsed_ms']}ms")
    
    # Example 3: Multiple generations with different temperatures
    print("\n[Example 3] Temperature variation (with rate limiting)")
    print("-" * 70)
    prompt = "GCTA"
    
    for temp in [0.5, 1.0]:  # Reduced to avoid rate limits
        result = api.generate(sequence=prompt, num_tokens=30, temperature=temp, retry_delay=3)
        if result:
            print(f"Temp {temp}: {result['sequence']}")
        else:
            print(f"Temp {temp}: Failed to generate")
    
    # Example 4: Batch processing with proper delays
    print("\n[Example 4] Batch processing")
    print("-" * 70)
    prompts = ["ATCG", "CGTA", "TACG"]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nBatch {i}/{len(prompts)}: {prompt}")
        result = api.generate(sequence=prompt, num_tokens=40, retry_delay=2)
        if result:
            print(f"  Result: {result['sequence']}")
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)


if __name__ == "__main__":
    # Set your API key as environment variable
    os.environ['NVIDIA_API_KEY'] = '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'
    
    main()