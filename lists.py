# Official problem lists, read from LeetCode's study plans and HackerRank's Python domain (Nov 2026).

TOP_150 = [
    ("Array / String", [88, 27, 26, 80, 169, 189, 121, 122, 55, 45, 274, 380, 238, 134, 135, 42, 13, 12, 58, 14, 151, 6, 28, 68]),
    ("Two Pointers", [125, 392, 167, 11, 15]),
    ("Sliding Window", [209, 3, 30, 76]),
    ("Matrix", [36, 54, 48, 73, 289]),
    ("Hashmap", [383, 205, 290, 242, 49, 1, 202, 219, 128]),
    ("Intervals", [228, 56, 57, 452]),
    ("Stack", [20, 71, 155, 150, 224]),
    ("Linked List", [141, 2, 21, 138, 92, 25, 19, 82, 61, 86, 146]),
    ("Binary Tree General", [104, 100, 226, 101, 105, 106, 117, 114, 112, 129, 124, 173, 222, 236]),
    ("Binary Tree BFS", [199, 637, 102, 103]),
    ("Binary Search Tree", [530, 230, 98]),
    ("Graph General", [200, 130, 133, 399, 207, 210]),
    ("Graph BFS", [909, 433, 127]),
    ("Trie", [208, 211, 212]),
    ("Backtracking", [17, 77, 46, 39, 52, 22, 79]),
    ("Divide & Conquer", [108, 148, 427, 23]),
    ("Kadane's Algorithm", [53, 918]),
    ("Binary Search", [35, 74, 162, 33, 34, 153, 4]),
    ("Heap", [215, 502, 373, 295]),
    ("Bit Manipulation", [67, 190, 191, 136, 137, 201]),
    ("Math", [9, 66, 172, 69, 50, 149]),
    ("1D DP", [70, 198, 139, 322, 300]),
    ("Multidimensional DP", [120, 64, 63, 5, 97, 72, 123, 188, 221]),
]

TOP_100_LIKED = [
    ("Hashing", [1, 49, 128, 560]),
    ("Two Pointers", [11, 15, 42, 283]),
    ("Sliding Window", [3, 76, 239, 438]),
    ("Matrix", [48, 54, 73, 240]),
    ("Linked Lists", [2, 19, 21, 23, 24, 25, 138, 141, 142, 146, 148, 160, 206, 234]),
    ("Binary Tree", [94, 98, 101, 102, 104, 105, 108, 114, 199, 226, 230, 236, 437, 543]),
    ("Graph", [200, 207, 994]),
    ("Trie", [208]),
    ("Backtracking", [17, 22, 39, 46, 51, 78, 79, 131]),
    ("Binary Search", [4, 33, 34, 35, 74, 124, 153]),
    ("Stack", [20, 84, 155, 394, 739]),
    ("Heap", [215, 295, 347]),
    ("Greedy", [45, 55, 121, 763]),
    ("Dynamic Programming", [5, 32, 62, 64, 70, 72, 118, 139, 152, 198, 279, 300, 322, 416, 1143]),
    ("Misc", [31, 41, 53, 56, 75, 136, 169, 189, 238, 287]),
]

HACKERRANK_PYTHON = [
    ("Introduction", ['Say "Hello, World!" With Python', "Python If-Else", "Arithmetic Operators", "Python: Division", "Loops", "Write a function", "Print Function"]),
    ("Basic Data Types", ["List Comprehensions", "Find the Runner-Up Score!", "Nested Lists", "Finding the percentage", "Lists", "Tuples"]),
    ("Strings", ["sWAP cASE", "String Split and Join", "What's Your Name?", "Mutations", "Find a string", "String Validators", "Text Alignment", "Text Wrap", "Designer Door Mat", "String Formatting", "Alphabet Rangoli", "Capitalize!", "The Minion Game", "Merge the Tools!"]),
    ("Sets", ["Introduction to Sets", "No Idea!", "Symmetric Difference", "Set .add()", "Set .discard(), .remove() & .pop()", "Set .union() Operation", "Set .intersection() Operation", "Set .difference() Operation", "Set .symmetric_difference() Operation", "Set Mutations", "The Captain's Room", "Check Subset", "Check Strict Superset"]),
    ("Math", ["Polar Coordinates", "Find Angle MBC", "Triangle Quest 2", "Mod Divmod", "Power - Mod Power", "Integers Come In All Sizes", "Triangle Quest"]),
    ("Itertools", ["itertools.product()", "itertools.permutations()", "itertools.combinations()", "itertools.combinations_with_replacement()", "Compress the String!", "Iterables and Iterators", "Maximize It!"]),
    ("Collections", ["collections.Counter()", "DefaultDict Tutorial", "Collections.namedtuple()", "Collections.OrderedDict()", "Word Order", "Collections.deque()", "Company Logo", "Piling Up!"]),
    ("Date and Time", ["Calendar Module", "Time Delta"]),
    ("Errors and Exceptions", ["Exceptions", "Incorrect Regex"]),
    ("Classes", ["Classes: Dealing with Complex Numbers", "Class 2 - Find the Torsional Angle"]),
    ("Built-Ins", ["Zipped!", "Input()", "Python Evaluation", "Athlete Sort", "Any or All", "ginortS"]),
    ("Python Functionals", ["Map and Lambda Function", "Validating Email Addresses With a Filter", "Reduce Function"]),
    ("Regex and Parsing", ["Detect Floating Point Number", "Re.split()", "Group(), Groups() & Groupdict()", "Re.findall() & Re.finditer()", "Re.start() & Re.end()", "Regex Substitution", "Validating Roman Numerals", "Validating phone numbers", "Validating and Parsing Email Addresses", "Hex Color Code", "HTML Parser - Part 1", "HTML Parser - Part 2", "Detect HTML Tags, Attributes and Attribute Values", "Validating UID", "Validating Credit Card Numbers", "Validating Postal Codes", "Matrix Script"]),
    ("XML", ["XML 1 - Find the Score", "XML2 - Find the Maximum Depth"]),
    ("Closures and Decorators", ["Standardize Mobile Number Using Decorators", "Decorators 2 - Name Directory"]),
    ("Numpy", ["Arrays", "Shape and Reshape", "Transpose and Flatten", "Concatenate", "Zeros and Ones", "Eye and Identity", "Array Mathematics", "Floor, Ceil and Rint", "Sum and Prod", "Min and Max", "Mean, Var, and Std", "Dot and Cross", "Inner and Outer", "Polynomials", "Linear Algebra"]),
    ("Debugging", ["Words Score", "Default Arguments"]),
]

assert sum(len(v) for _, v in TOP_150) == 150
assert sum(len(v) for _, v in TOP_100_LIKED) == 100
assert sum(len(v) for _, v in HACKERRANK_PYTHON) == 115

# LeetCode URL slugs that differ from a plain slug of the title.
LC_SLUG_OVERRIDES = {50: "powx-n", 69: "sqrtx", 118: "pascals-triangle", 380: "insert-delete-getrandom-o1"}

# HackerRank challenge slugs, in the same order as HACKERRANK_PYTHON.
HR_SLUGS = """py-hello-world py-if-else python-arithmetic-operators python-division python-loops write-a-function python-print
list-comprehensions find-second-maximum-number-in-a-list nested-list finding-the-percentage python-lists python-tuples
swap-case python-string-split-and-join whats-your-name python-mutations find-a-string string-validators text-alignment text-wrap designer-door-mat python-string-formatting alphabet-rangoli capitalize the-minion-game merge-the-tools
py-introduction-to-sets no-idea symmetric-difference py-set-add py-set-discard-remove-pop py-set-union py-set-intersection-operation py-set-difference-operation py-set-symmetric-difference-operation py-set-mutations py-the-captains-room py-check-subset py-check-strict-superset
polar-coordinates find-angle triangle-quest-2 python-mod-divmod python-power-mod-power python-integers-come-in-all-sizes python-quest-1
itertools-product itertools-permutations itertools-combinations itertools-combinations-with-replacement compress-the-string iterables-and-iterators maximize-it
collections-counter defaultdict-tutorial py-collections-namedtuple py-collections-ordereddict word-order py-collections-deque most-commons piling-up
calendar-module python-time-delta exceptions incorrect-regex class-1-dealing-with-complex-numbers class-2-find-the-torsional-angle
zipped input python-eval python-sort-sort any-or-all ginorts map-and-lambda-expression validate-list-of-email-address-with-filter reduce-function
introduction-to-regex re-split re-group-groups re-findall-re-finditer re-start-re-end re-sub-regex-substitution validate-a-roman-number validating-the-phone-number validating-named-email-addresses hex-color-code html-parser-part-1 html-parser-part-2 detect-html-tags-attributes-and-attribute-values validating-uid validating-credit-card-number validating-postalcode matrix-script
xml-1-find-the-score xml2-find-the-maximum-depth standardize-mobile-number-using-decorators decorators-2-name-directory
np-arrays np-shape-reshape np-transpose-and-flatten np-concatenate np-zeros-and-ones np-eye-and-identity np-array-mathematics floor-ceil-and-rint np-sum-and-prod np-min-and-max np-mean-var-and-std np-dot-and-cross np-inner-and-outer np-polynomials np-linear-algebra
words-score default-arguments""".split()
assert len(HR_SLUGS) == 115
