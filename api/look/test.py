import asyncio

async def test_loop():
    print("Test loop started")
    while True:
        await asyncio.sleep(1)
        print("Test loop is running")

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(test_loop())

    print("Main function running")
    # Run indefinitely to keep the loop alive
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())