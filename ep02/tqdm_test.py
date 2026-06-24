import time
import tqdm


for i in tqdm.tqdm(range(10000)):
    print(i)
    time.sleep(0.1)  # 模擬處理時間
