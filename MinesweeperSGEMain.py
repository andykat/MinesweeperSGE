import Minesweeper.MineSweeper as Mine
import Minesweeper.MinesweeperSGE as sge
# m = Mine.Mines(size = 5, minesN = 5)
# m.printBoard()
# m.selectZeroFirst()
# print("\n\n\n")
# m.printPBoard()
# m.select(0,0,"click")
# m.drawSomething()
# while True:
#     a= 1
#
ge = sge.MinesweeperSGE()
ge.populationSize = 50
ge.recursionMax = 8
ge.read_bnf_file("minesweeper.bnf")
bestResults=ge.runIterations(40)
for i in range(0,5):
    phen = ge.translateSeqToPhenotype(bestResults[0][i])[0][0]
    code = ge.translateObjectsIntoCode(phen)
    print(code)
    print(str(bestResults[1][i]))
    print("\n\n")
# ge.initializePopulation()
# # print(ge.geneExpansionCount)
# # print(ge.currentPopulation[0])
# tuple = ge.translateSeqToPhenotype(ge.currentPopulation[0])
# # print(tuple)
# objects = tuple[0][0]
# code = ge.translateObjectsIntoCode(objects)
# print(code)
# fitness = ge.minesweeperFitness(code)
# print(fitness)
