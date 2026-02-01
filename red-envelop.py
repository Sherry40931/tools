sherry = 8800 * 2
peter1 = 6000 * 2
peter2 = 2600 * 2


def check(a, b):
    return a * 1000 + b * 500


def loop_person(target: int) -> list[list[int]]:
    result = []
    for i in range(0, 50, 2):
        for j in range(0, 20, 2):
            c = check(i, j)
            if c > target:
                continue
            k = (target - c) / 100
            if k > 50:
                continue

            if int(k) == k:
                result.append([i, j, int(k)])
    return result


result_sherry = loop_person(sherry)
result_peter1 = loop_person(peter1)
result_peter2 = loop_person(peter2)

valid_combinations = []
for i in range(len(result_sherry)):
    for j in range(len(result_peter1)):
        for k in range(len(result_peter2)):
            a1, b1, c1 = result_sherry[i]
            a2, b2, c2 = result_peter1[j]
            a3, b3, c3 = result_peter2[k]

            count1 = (a1 + b1 + c1) // 2
            count2 = (a2 + b2 + c2) // 2
            count3 = (a3 + b3 + c3) // 2

            # 每種面額都有
            if any(x == 0 for x in [a1, b1, c1, a2, b2, c2, a3, b3, c3]):
                continue

            # 不要尾數是 4
            if any(x % 10 == 4 for x in [count1, count2, count3]):
                continue

            # 吉利分數
            score = 0
            # 總數量為偶數加分
            score += (count1 % 2 == 0) + (count2 % 2 == 0) + (count3 % 2 == 0)
            # 每張面額為偶數加分
            score += (a1 % 4 == 0) + (b1 % 4 == 0) + (c1 % 4 == 0)
            score += (a2 % 4 == 0) + (b2 % 4 == 0) + (c2 % 4 == 0)
            score += (a3 % 4 == 0) + (b3 % 4 == 0) + (c3 % 4 == 0)
            # 若面額數量為 4 扣分
            score -= (a1 == 4) + (b1 == 4) + (c1 == 4)
            score -= (a2 == 4) + (b2 == 4) + (c2 == 4)
            score -= (a3 == 4) + (b3 == 4) + (c3 == 4)

            if (a1 + a2 + a3 < 50) and (b1 + b2 + b3 < 20) and (c1 + c2 + c3 < 50):
                valid_combinations.append(
                    (result_sherry[i], result_peter1[j], result_peter2[k], score)
                )

if valid_combinations:
    valid_combinations.sort(key=lambda x: x[3], reverse=True)
    for idx, (sherry_combo, peter_combo_part1, peter_combo_part2, score) in enumerate(
        valid_combinations, 1
    ):
        a1, b1, c1 = sherry_combo
        a2, b2, c2 = peter_combo_part1
        a3, b3, c3 = peter_combo_part2
        print(
            f"{idx}. score: {score} | "
            f"Sherry: 1000×{a1} + 500×{b1} + 100×{c1}, count: {(a1 + b1 + c1) // 2} | "
            f"Peter (6000): 1000×{a2} + 500×{b2} + 100×{c2}, count: {(a2 + b2 + c2) // 2} | "
            f"Peter (2600): 1000×{a3} + 500×{b3} + 100×{c3}, count: {(a3 + b3 + c3) // 2} | "
            f"Total: 1000×{a1+a2+a3}, 500×{b1+b2+b3}, 100×{c1+c2+c3}, amount: {1000*(a1+a2+a3) + 500*(b1+b2+b3) + 100*(c1+c2+c3)}"
        )
else:
    print("No valid combinations found that satisfy the criteria.")
