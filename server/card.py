import random
import json

class PlayCard(dict):
    def __init__(self):
        numbers = random.sample(range(1, 90), 15)
        rows = []
        rows.append(numbers[:5])
        rows.append(numbers[5:10])
        rows.append(numbers[10:15])

        dict.__init__(self, gamecard=rows)
        self.gamecard = rows

    def calculateCinkos(self, oldNumbers):
        total = 0
        for row in self.gamecard:
            intersection = list(set(row) & set(oldNumbers))
            if len(intersection) == len(row):
                total += 1
        return total
