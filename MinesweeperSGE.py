import random
import copy
import Minesweeper.MineSweeper as Mine
class MinesweeperSGE:

    def __init__(self):
        self.rules = []
        self.nonTerminals = []
        random.seed()
        self.populationSize = 100
        self.genotypeMax = 99999999 #maximum value for each integer
        self.genotypeMin = 0 #minimum value for each integer

        self.tournamentK = 5 #number of entrants for each tournament
        self.tournamentP = 0.8 #probability of selecting winner
        self.topPerformingCarry = 3 #number of top performing sequences from previous population carried over


        self.letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
        self.geneMutationChance = 0.25
        self.averageBestFitness = []
        self.averageBestFitnessN = 5

        self.recursionMax = 20

        self.minesweeperSize = 5
        self.minesN = 5

    #read the grammar bnf file
    def read_bnf_file(self, file_name):
        equationSplit = "::="

        for line in open(file_name, 'r'):
            #take lefthand
            if line.startswith("<") and equationSplit in line:
                tSplit = line.split(equationSplit)
                lhs = tSplit[0].strip()
                rhs = tSplit[1].strip().replace("\n","")

                #transform rhs into orGroup of expressions
                orSeparatedList = rhs.split("|")

                o = OrGroup()
                for production in orSeparatedList:
                    expression = production.split("_")
                    e = Expression()
                    for obj in expression:
                        if obj != "":
                            if "<" in obj:
                                e.appendObject(obj,"nt")
                            else:
                                e.appendObject(obj,"t")

                    o.expressions.append(e)

                self.rules.append(Rule(lhs, o))
        self.finalNonTerminal = self.rules[0].lhs
        self.processGrammarRecursion()
        for rule in self.rules:
            print("lhs:" + rule.lhs)
            for expression in rule.rhs.expressions:
                for ob in expression.objects:
                    print(ob + " ",end='')
                print("| ", end='')
            print("\n")

        for rule in self.rules:
            self.nonTerminals.append(rule.lhs)

        self.countReferences()
        self.calculateExpansions()

    def processGrammarRecursion(self):
        ruleIndex = 0
        while ruleIndex < len(self.rules):
            lhs = self.rules[ruleIndex].lhs
            orGroup = self.rules[ruleIndex].rhs
            flag = False
            for expression in orGroup.expressions:
                if flag:
                    break
                for i in range(0, len(expression.objects)):
                    if expression.objects[i] == lhs and expression.objectTypes[i] == "nt":
                        flag = True
                        break

            if flag:
                #recursion found
                for i in range(0, self.recursionMax):
                    orGroupDeepCopy = copy.deepcopy(orGroup)
                    newOrGroup = copy.deepcopy(orGroup)
                    newlhs = lhs
                    #append lvl-1 to the lfh expression
                    if i > 0:
                        newlhs = self.appendLevelToNonTerminal(lhs, i-1)
                    newNT = self.appendLevelToNonTerminal(lhs, i)
                    if i <self.recursionMax - 1:
                        for j in range(0,len(orGroupDeepCopy.expressions)):
                            expression = orGroupDeepCopy.expressions[j]
                            for k in range(0, len(expression.objects)):
                                if expression.objects[k] == lhs and expression.objectTypes[k] == "nt":
                                    newOrGroup.expressions[j].objects[k] = newNT

                    else:
                        #for the last level, we must replace the recursive nonterminal with all possible nonrecursive results
                        newNTexp = []
                        hasNTIndices = []
                        hasNTIndicesReverse = []
                        for j in range(0,len(orGroupDeepCopy.expressions)):
                            expression = orGroupDeepCopy.expressions[j]
                            hasNT = False
                            for k in range(0, len(expression.objects)):
                                if expression.objects[k] == lhs and expression.objectTypes[k] == "nt":
                                    hasNT = True
                            #does not contain the nonterminal, so we save the result
                            if hasNT == False:
                                newNTexp.append(copy.deepcopy(expression))
                            else:
                                hasNTIndices.append(j)
                                hasNTIndicesReverse.insert(0, j)
                            for j in range(0, len(orGroupDeepCopy.expressions)):
                                expression = orGroupDeepCopy.expressions[j]
                                for k in range(0, len(expression.objects)):
                                    if expression.objects[k] == lhs and expression.objectTypes[k] == "nt":
                                        newOrGroup.expressions[j].objects[k] = newNT

                        # remove existing expressions in our newOrGroup because we will adding new ones
                        for j in range(0, len(hasNTIndicesReverse)):
                            newOrGroup.expressions.pop(hasNTIndicesReverse[j])

                        # add new expressions
                        for j in range(0,len(hasNTIndices)):
                            for k in range(0, len(newNTexp)):
                                newexpression = copy.deepcopy(orGroupDeepCopy.expressions[hasNTIndices[j]])
                                replaceexp = copy.deepcopy(newNTexp[k])
                                newexpIndex = 0
                                while newexpIndex < len(newexpression.objects):
                                    if newexpression.objects[newexpIndex] == lhs and newexpression.objectTypes[newexpIndex] == "nt":
                                        newexpression.objects.pop(newexpIndex)
                                        newexpression.objectTypes.pop(newexpIndex)
                                        for l in range(0, len(replaceexp.objects)):
                                            newexpression.objects.insert(newexpIndex + l, replaceexp.objects[l])
                                            newexpression.objectTypes.insert(newexpIndex + l, replaceexp.objectTypes[l])
                                    else:
                                        newexpIndex += 1
                                newOrGroup.expressions.append(newexpression)

                    self.rules.insert(ruleIndex + i + 1, Rule(newlhs, newOrGroup))
                self.rules.pop(ruleIndex)
            else:
                #recursion not found
                ruleIndex += 1
    def appendLevelToNonTerminal(self, stri, level):
        position = stri.find('>')
        if position < 0:
            print("error: > not found in nonterminal")
        else:
            newstr = stri[:position] + "lvl" + str(level) + stri[position:]

        return newstr
    #counts the max number of times a left hand sided terminal can expand into each nonterminal
    def countReferences(self):
        self.referencesCount = {}

        for refnt in self.nonTerminals:
            #create dictionary for lhs nonterminal
            self.referencesCount[refnt] = {}
            for rule in self.rules:
                #look for the rule where refnt is expanded
                if rule.lhs == refnt:
                    for exp in rule.rhs.expressions:
                        #creates dictionary for rhs nonterminals
                        count = {}
                        for i in range(0, len(exp.objects)):
                            if exp.objectTypes[i] == "nt":
                                if exp.objects[i] in count:
                                    count[exp.objects[i]] += 1
                                else:
                                    count[exp.objects[i]] = 1

                        for key in count.keys():
                            if key in self.referencesCount[refnt]:
                                if count[key] > self.referencesCount[refnt][key]:
                                    self.referencesCount[refnt][key] = count[key]
                            else:
                                self.referencesCount[refnt][key] = count[key]
        # print(self.referencesCount)

    # counts the number of expansions per nonterminal
    def calculateExpansions(self):
        #count of each nonterminal
        terminalCount = {}
        self.geneExpansionCount = {}
        for refnt in self.nonTerminals:
            if refnt == self.rules[0].lhs:
                terminalCount = self.referencesCount[refnt]
                self.geneExpansionCount[refnt] = 1
            else:
                #number of times refnt is expanded
                refntCount = terminalCount[refnt]
                self.geneExpansionCount[refnt] = refntCount

                #for each nt that refnt references, we add the
                # product of the referencecount for nt and the number of times refnt is expanded
                # to the terminal Count
                for nt in self.referencesCount[refnt].keys():
                    if nt in terminalCount:
                        terminalCount[nt] += self.referencesCount[refnt][nt] * refntCount
                    else:
                        terminalCount[nt] = self.referencesCount[refnt][nt] * refntCount
        # print(self.geneExpansionCount)
    def initializePopulation(self):
        self.currentPopulation = []
        self.fitness = []
        for i in range(0, self.populationSize):
            geneDict = {}
            for key in self.geneExpansionCount:
                genotypeMaxLength = self.geneExpansionCount[key]
                geneDict[key] = []
                for j in range(0, genotypeMaxLength):
                    geneDict[key].append(self.randomGenotype())
            self.currentPopulation.append(geneDict)
            self.fitness.append(0)

    def randomGenotype(self):
        return random.randint(self.genotypeMin, self.genotypeMax)

    def recombination(self, parents, nonterminalCounts):
        child = {}
        mutatedParents = []

        for parent in parents:
            mutatedParents.append(copy.deepcopy(parent))
        #mutate genes
        for i in range(0, len(mutatedParents)):
            mutatedParents[i] = self.mutateParent(mutatedParents[i], nonterminalCounts[i])
        for nt in self.nonTerminals:
            randN = random.randint(0, 1)
            child[nt] = copy.deepcopy(mutatedParents[randN][nt])
        return child
    def mutateParent(self, parent, nonterminalCount):
        for nt in self.nonTerminals:
            chance = random.uniform(0, 1)
            if chance<self.geneMutationChance:
                if nonterminalCount[nt] > 0:
                    randIndex = random.randint(0, nonterminalCount[nt]-1)
                    parent[nt][randIndex] = self.randomGenotype()
        return parent
    def recombinationCross(self, parents, nonterminalCounts):
        child = [{},{}]
        mutatedParents = []
        for parent in parents:
            mutatedParents.append(copy.deepcopy(parent))
        #mutate genes
        for i in range(0, len(mutatedParents)):
            mutatedParents[i] = self.mutateParent(mutatedParents[i], nonterminalCounts[i])

        for nt in self.nonTerminals:
            randN = random.randint(0, 1)
            max = nonterminalCounts[randN][nt]
            # crossoverPoint = random.randint(0, len(parents[randN][nt]) - 1)
            if max == 0:
                max = random.randint(0, len(parents[randN][nt]) - 1)
            crossoverPoint = random.randint(0, max)
            otherN = randN + 1
            if otherN == 2:
                otherN = 0
            child[0][nt] = []
            child[1][nt] = []

            child[0][nt] = child[0][nt] + copy.deepcopy(mutatedParents[randN][nt])[:crossoverPoint]
            child[0][nt] = child[0][nt] + copy.deepcopy(mutatedParents[otherN][nt])[crossoverPoint:]
            child[1][nt] = child[1][nt] + copy.deepcopy(mutatedParents[otherN][nt])[:crossoverPoint]
            child[1][nt] = child[1][nt] + copy.deepcopy(mutatedParents[randN][nt])[crossoverPoint:]

        return child
    def mutation(self, seq):
        for nt in self.nonTerminals:
            chance = random.uniform(0, 1)
            if chance<self.geneMutationChance:
                randIndex = random.randint(0, len(seq[nt])-1)
                seq[nt][randIndex] = self.randomGenotype()
        return seq

    def translateSeqToPhenotype(self, genes, removeNonterminals=True):
        curObjects = []
        curObjectTypes = []
        curObjects.append(self.finalNonTerminal)
        curObjectTypes.append("nt")
        nonTerminalCount = {}
        for nt in self.nonTerminals:
            nonTerminalCount[nt] = 0
        while "nt" in curObjectTypes:
            #find next non terminal
            nonTerminalObject = ""
            nonTerminalIndex = -1
            for i in range(0,len(curObjectTypes)):
                if curObjectTypes[i] == "nt":
                    nonTerminalObject = curObjects[i]

                    nonTerminalIndex = i
                    break
            if nonTerminalIndex < 0:
                print("no terminalfound")
                break
            # print(curObjects)
            # print(nonTerminalObject)
            for rule in self.rules:
                #found the specific rule
                if rule.lhs == nonTerminalObject:
                    orGroup = rule.rhs
                    nOrGroups = len(orGroup.expressions)

                    #select an expression from or groups
                    value = genes[nonTerminalObject][nonTerminalCount[nonTerminalObject]]
                    nonTerminalCount[nonTerminalObject] += 1
                    index = value % nOrGroups
                    expression = orGroup.expressions[index]
                    #replace non terminal with new expression
                    curObjects.pop(nonTerminalIndex)
                    curObjectTypes.pop(nonTerminalIndex)
                    for i in range(0,len(expression.objects)):
                        curObjects.insert(nonTerminalIndex + i, expression.objects[i])
                        curObjectTypes.insert(nonTerminalIndex + i, expression.objectTypes[i])

        if removeNonterminals:
            i = 0
            while i < len(curObjects):
                if curObjectTypes[i] == "nt":
                    curObjects.pop(i)
                    curObjectTypes.pop(i)
                    i -= 1
                i += 1
                return [[curObjects, curObjectTypes], nonTerminalCount]

        return [[curObjects, curObjectTypes], nonTerminalCount]

    #returns a tournament selected genotype
    def tournamentSelection(self, k):
        selected = []
        for i in range(0,k):
            selected.append(random.randint(0,self.populationSize-1))
        selected = sorted(selected)

        for i in range(0, k):
            x = random.uniform(0,1)
            if x < self.tournamentP:
                # return self.currentPopulation[self.fitnessIndices[selected[i]][0]]
                return self.fitnessIndices[selected[i]][0]
        # return self.currentPopulation[self.fitnessIndices[selected[0]][0]]
        return self.fitnessIndices[selected[0]][0]

    def createChildren(self):
        parents = []
        parent0index = self.tournamentSelection(self.tournamentK)
        parent1index = self.tournamentSelection(self.tournamentK)
        parents.append(self.currentPopulation[parent0index])
        parents.append(self.currentPopulation[parent1index])
        nonterminalCounts = []
        nonterminalCounts.append(self.populationNonterminalCount[parent0index])
        nonterminalCounts.append(self.populationNonterminalCount[parent1index])
        children = self.recombinationCross(parents, nonterminalCounts)
        return children


    def runIterations(self, iterations):
        self.initializePopulation()
        self.averageBestFitness = []
        #run the iterations
        for i in range(0, iterations):
            if i%10==0:
                print(i)
            print("iteration: " + str(i))
            self.step()

        #get highest performers
        for i in range(0, self.populationSize):
            seq = self.currentPopulation[i]
            phen = self.translateSeqToPhenotype(seq, removeNonterminals=True)[0][0]
            code = self.translateObjectsIntoCode(phen)
            self.fitness[i] = self.minesweeperFitness(code)
            # get the top performing sequences

        self.fitnessIndices = []
        for i in range(0, self.populationSize):
            self.fitnessIndices.append([i, self.fitness[i]])

        sorted(self.fitnessIndices, key=lambda x: x[1], reverse=True)
        self.highestPerformers = []
        self.highestFitnesses = []
        numberOfTopPerformers = 5

        for i in range(0, numberOfTopPerformers):
            self.highestPerformers.append(self.currentPopulation[self.fitnessIndices[i][0]])
            self.highestFitnesses.append(self.fitnessIndices[i][1])

        return [self.highestPerformers, self.highestFitnesses]

    def step(self):
        phens = []
        self.populationNonterminalCount = []
        #get the fitness of all sequences
        for i in range(0, self.populationSize):
            seq = self.currentPopulation[i]
            result = self.translateSeqToPhenotype(seq, removeNonterminals=True)
            phen = result[0][0]
            nonTerminalCount = result[1]
            self.populationNonterminalCount.append(nonTerminalCount)
            code = self.translateObjectsIntoCode(phen)
            # self.fitness[i] = self.harmonicFitness(phen)
            self.fitness[i] = self.minesweeperFitness(code)

        #get the top performing sequences

        self.fitnessIndices = []
        for i in range(0, self.populationSize):
            self.fitnessIndices.append([i, self.fitness[i]])

        self.fitnessIndices = sorted(self.fitnessIndices, key=lambda x: x[1], reverse=True)

        afitness = 0.0
        for i in range(0, self.averageBestFitnessN):
            afitness += self.fitnessIndices[i][1]
        afitness /= -float(self.averageBestFitnessN)
        self.averageBestFitness.append(afitness)


        self.newpopulation = []

        #add the best performing sequence from last population
        for i in range(0, self.topPerformingCarry):
            self.newpopulation.append(copy.deepcopy(self.currentPopulation[self.fitnessIndices[i][0]]))

        #fill in the rest of the new population with children
        while len(self.newpopulation) < self.populationSize:
            #crossed children
            children = self.createChildren()

            self.newpopulation.append(children[0])
            if len(self.newpopulation) < self.populationSize:
                self.newpopulation.append(children[1])

        # print top performers
        for i in range(0, 3):
            phen = self.translateSeqToPhenotype(self.currentPopulation[self.fitnessIndices[i][0]])[0][0]
            stri = ""
            # for o in phen:
            #     stri = stri + o
            print(stri + ":" + str(self.fitnessIndices[i][1]) + "   seqlength:" + str(len(self.currentPopulation[self.fitnessIndices[i][0]])) )

        self.currentPopulation = self.newpopulation

    #translate the phenotype into code. Appends necessary initializations at the beginning
    #and an answer saving function at the end
    def translateObjectsIntoCode(self, objects):
        code = ""
        for s in objects:
            code += s
        code = "\n" + code
        indentation = 0
        flag = False
        code = code.replace("less", "<")
        code = code.replace("greater", ">")
        while not flag:
            newLineIndex = code.find("\\n")
            if newLineIndex < 0:
                flag = True
                break
            else:
                # print(code[newLineIndex+2])
                if code[newLineIndex+2] == '{':
                    indentation += 1
                    code = code[:newLineIndex+2] + code[newLineIndex+3:]
                elif code[newLineIndex-1] == '}':
                    indentation -= 1
                    code = code[:newLineIndex-1] + code[newLineIndex:]
                    newLineIndex -= 1
                tabs = ""
                for i in range(0, indentation):
                    tabs += "\t"
                code = code[:newLineIndex] + "\n" + tabs + code[newLineIndex+2:]

        # add code to front
        varInitCode = "i=0\nj=0\nk=0\nansX=0\nansY=0\naction=0\nsize=" + str(self.minesweeperSize) + "\n"
        # a array set
        arrayInitCode = "a=[]\nfor i in range(0,5):\n\ta.append(0)\n"
        endCode = "\nself.saveCodeAnswers(ansX, ansY, action)"
        code = varInitCode + arrayInitCode + code + endCode
        return code

    def saveCodeAnswers(self, ansX, ansY, action):
        self.ansX = ansX
        self.ansY = ansY
        self.action = action

    #calculates the fitness of the program by using it to play minesweeper
    def minesweeperFitness(self, code):
        flag = True
        m = Mine.Mines(size = self.minesweeperSize, minesN = self.minesN)
        m.selectZeroFirst()
        count = 0
        #repeatedly run the code to get moves, and see if the move is valid
        #keep count of the number of successful moves
        while flag:
            try:
                exec(code)
                action = "click"
                if self.action == 1:
                    action = "flag"
                # tString = str(self.ansX) + ", " + str(self.ansY) + "\t" + action
                # print(tString)
                flag = m.select(self.ansX, self.ansY, action)
                count += 1
            except IndexError:
                # print("indexError")
                flag = False

        #normalize the fitness by making it between 0 and 1
        return float(count)/float(self.minesweeperSize)/float(self.minesweeperSize)

class Rule:
    #lhs is a nonterminal
    #rhs is an OrGroup of Expressions
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
class OrGroup:
    def __init__(self):
        self.expressions = []

class Expression:
    def __init__(self):
        self.objects = []
        self.objectTypes = []
        #self.nonterminals = []
        #self.terminals = []
    def appendObject(self, object, objectType):
        self.objects.append(object)
        self.objectTypes.append(objectType)
    def removeObjectAtIndex(self, index):
        self.objects.remove(index)
        self.objectTypes.remove(index)
    def insertObjectAtIndex(self, object, objectType, index):
        self.objects.insert(index, object)
        self.objectTypes.insert(index, objectType)

    def __hash__(self):
        str = ""
        for obj in self.objects:
            str = str + obj
        return hash(str)

    def __eq__(self, other):
        return (self.__hash__()) == (other.__hash__())

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)
class BracketGroup:
    def __init__(self, expression):
        self.expression = expression



