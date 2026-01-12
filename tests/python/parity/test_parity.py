import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))


PYTHON_API_URL = "http://localhost:8000"
DOTNET_API_URL = "http://localhost:5000"
TEST_QUERY = "who is the best candidate for java?"


async def test_python_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PYTHON_API_URL}/chat",
                json={"question": TEST_QUERY},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Python API error: {e}")
            return None


async def test_dotnet_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{DOTNET_API_URL}/chat",
                json={"question": TEST_QUERY},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ .NET API error: {e}")
            return None


async def run_parity_test():
    print("="*80)
    print("PYTHON vs .NET PARITY TEST")
    print("="*80)
    print(f"\nTest Query: '{TEST_QUERY}'")
    print("\n" + "-"*80)
    
    print("\nTesting Python API...")
    python_result = await test_python_api()
    
    print("\nTesting .NET API...")
    dotnet_result = await test_dotnet_api()
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    if not python_result:
        print("❌ Python API failed or returned no data")
        return False
    
    if not dotnet_result:
        print("❌ .NET API failed or returned no data")
        return False
    
    print("\n✅ Python API Response:")
    print(f"  Answer: {python_result.get('answer', 'N/A')[:100]}...")
    print(f"  Sources count: {len(python_result.get('sources', []))}")
    print(f"  Metadata: {python_result.get('metadata', {}).get('selected_candidate', {}).get('fullname', 'N/A')}")
    
    print("\n✅ .NET API Response:")
    print(f"  Answer: {dotnet_result.get('answer', 'N/A')[:100]}...")
    
    dotnet_sources = dotnet_result.get('sources', [])
    if isinstance(dotnet_sources, str):
        print(f"  ❌ Sources is STRING (should be array): {dotnet_sources[:50]}...")
        dotnet_sources_count = 0
    else:
        dotnet_sources_count = len(dotnet_sources)
        print(f"  ✅ Sources is ARRAY with {dotnet_sources_count} items")
    
    dotnet_metadata = dotnet_result.get('metadata')
    if dotnet_metadata:
        selected = dotnet_metadata.get('selected_candidate', {})
        print(f"  Metadata: {selected.get('fullname', 'N/A')}")
    else:
        print(f"  Metadata: None")
    
    print("\n" + "="*80)
    print("PARITY CHECKS")
    print("="*80)
    
    checks_passed = []
    checks_failed = []
    
    python_answer = python_result.get('answer', '')
    dotnet_answer = dotnet_result.get('answer', '')
    
    if "No candidates found" in python_answer and "No candidates found" in dotnet_answer:
        checks_failed.append("Both APIs returned 'No candidates found' - filter bug not fixed")
    elif "No candidates found" not in python_answer and "No candidates found" not in dotnet_answer:
        checks_passed.append("Both APIs returned candidates (not empty)")
    else:
        checks_failed.append(f"Mismatch: Python empty={('No candidates' in python_answer)}, .NET empty={('No candidates' in dotnet_answer)}")
    
    python_sources_count = len(python_result.get('sources', []))
    if isinstance(dotnet_sources, list):
        checks_passed.append(f"✅ .NET sources is array (was string)")
    else:
        checks_failed.append(f"❌ .NET sources is still string, not array")
    
    if python_sources_count > 0 and dotnet_sources_count > 0:
        checks_passed.append(f"✅ Both APIs returned sources (Python={python_sources_count}, .NET={dotnet_sources_count})")
    elif python_sources_count == 0 and dotnet_sources_count == 0:
        checks_passed.append("Both APIs returned no sources")
    else:
        checks_failed.append(f"❌ Sources count mismatch (Python={python_sources_count}, .NET={dotnet_sources_count})")
    
    python_fullname = python_result.get('metadata', {}).get('selected_candidate', {}).get('fullname', '')
    dotnet_fullname = ''
    if dotnet_metadata:
        dotnet_fullname = dotnet_metadata.get('selected_candidate', {}).get('fullname', '')
    
    if python_fullname and dotnet_fullname:
        if python_fullname == dotnet_fullname:
            checks_passed.append(f"✅ Both selected same candidate: {python_fullname}")
        else:
            checks_failed.append(f"❌ Different candidates (Python={python_fullname}, .NET={dotnet_fullname})")
    
    print("\nPassed:")
    for check in checks_passed:
        print(f"  {check}")
    
    if checks_failed:
        print("\nFailed:")
        for check in checks_failed:
            print(f"  {check}")
    
    print("\n" + "="*80)
    if not checks_failed:
        print("✅ ALL PARITY CHECKS PASSED")
    else:
        print(f"❌ {len(checks_failed)} PARITY CHECKS FAILED")
    print("="*80)
    
    return len(checks_failed) == 0


if __name__ == "__main__":
    success = asyncio.run(run_parity_test())
    sys.exit(0 if success else 1)
