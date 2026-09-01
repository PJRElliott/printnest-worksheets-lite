#!/usr/bin/env python3
"""
PrintNest 汎用 Etsy サムネ7枚生成。

各本固有のページレプリカ画像なしで、タイトル・特徴・カラーパレットで
魅力的なサムネを構築する。本ごとの設定は meta.json から取得。

Usage:
  python3 make_thumbnails_universal.py --book sightwords
  python3 make_thumbnails_universal.py --book mazes_kids
  python3 make_thumbnails_universal.py --book sudoku
  python3 make_thumbnails_universal.py --book wordsearch
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Install Pillow: pip3 install Pillow")

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path.home() / "Desktop" / "PrintNest"

CANVAS_SIZE = (2000, 2000)
FONT_REGULAR = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

# 本ごとの色テーマ＋表紙文字＋特徴リスト
BOOK_CONFIG = {
    "sightwords": {
        "primary": (139, 92, 246),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Sight Words",
        "title_main": "100",
        "subtitle": "Pre-K & Kindergarten Workbook",
        "tagline": "Trace · Read · Spell · Use in Sentences",
        "ages_badge": "AGES 4-6",
        "decorations": [("the", (139, 92, 246)), ("and", (245, 158, 11)),
                        ("you", (16, 185, 129)), ("play", (236, 72, 153)),
                        ("look", (59, 130, 246))],
        "features": [
            "100 high-frequency sight words",
            "50 tracing pages (2 words each)",
            "Find the word activities",
            "Color the words decoration",
            "Sentence building practice",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten",
            "Homeschool families",
            "Reading intervention",
            "Early literacy practice",
        ],
    },
    "mazes_kids": {
        "primary": (16, 185, 129),
        "accent": (245, 158, 11),
        "soft_top": (209, 250, 229),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Kids Mazes",
        "title_main": "100",
        "subtitle": "Fun Maze Puzzles Activity Book",
        "tagline": "Easy · Medium · Hard · Expert",
        "ages_badge": "AGES 4-10",
        "decorations": [],
        "features": [
            "100 unique maze puzzles",
            "30 Easy mazes (8x8)",
            "30 Medium mazes (10x10)",
            "25 Hard mazes (12x12)",
            "15 Expert mazes (15x15)",
        ],
        "perfect_for": [
            "Ages 4-10 kids",
            "Road trip activity",
            "Homeschool brain break",
            "Screen-free fun",
        ],
    },
    "sudoku": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (233, 213, 255),
        "bg": (252, 248, 240),
        "title_top": "Sudoku",
        "title_main": "65",
        "subtitle": "Puzzle Book · Easy to Expert",
        "tagline": "Printable Adult Brain Game Workbook",
        "ages_badge": "FOR ADULTS",
        "decorations": [],
        "features": [
            "65 unique sudoku puzzles",
            "20 Easy puzzles",
            "20 Medium puzzles",
            "15 Hard puzzles",
            "10 Expert puzzles",
        ],
        "perfect_for": [
            "Adult brain training",
            "Senior cognitive activity",
            "Travel companion",
            "Daily mental fitness",
        ],
    },
    "wordsearch": {
        "primary": (236, 72, 153),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Word Search",
        "title_main": "50",
        "subtitle": "Themed Puzzles · Family Friendly",
        "tagline": "Animals · Holidays · Sports · Nature · and more!",
        "ages_badge": "FOR ALL AGES",
        "decorations": [],
        "features": [
            "50 themed word search puzzles",
            "15x15 grids · 8 directions",
            "12-13 words per puzzle",
            "Holiday & seasonal themes",
            "Complete answer keys included",
        ],
        "perfect_for": [
            "Family game nights",
            "Kids 8+, teens, adults",
            "Travel & road trips",
            "Senior brain training",
        ],
    },
    "word_scramble": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Word Scramble",
        "title_main": "50",
        "subtitle": "Themed Puzzles · 500+ Words to Unscramble",
        "tagline": "Animals · Food · Sports · Nature · Holidays · and more!",
        "ages_badge": "FOR ALL AGES",
        "decorations": [],
        "features": [
            "50 themed word scramble puzzles",
            "10 words per puzzle · 500+ words total",
            "Hint provided as theme name",
            "Complete answer keys included",
            "Printable on standard letter paper",
        ],
        "perfect_for": [
            "Family game nights",
            "Kids 8+, teens, adults",
            "Travel & road trips",
            "Classroom & homeschool",
        ],
    },
    "multiplication": {
        "primary": (124, 58, 237),
        "accent": (245, 158, 11),
        "soft_top": (237, 233, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Multiplication",
        "title_main": "× 1-12",
        "subtitle": "Times Tables Practice Workbook",
        "tagline": "1000+ Problems · Grades 2-4 · Answer Key",
        "ages_badge": "GRADES 2-4",
        "decorations": [],
        "features": [
            "Complete times tables chart 1-12",
            "24 times table practice pages",
            "20 mixed practice sets",
            "1000+ multiplication problems",
            "Full answer key included",
        ],
        "perfect_for": [
            "2nd-4th grade students",
            "Homeschool math practice",
            "Times tables mastery",
            "Daily math drills",
        ],
    },
    "addition_subtraction": {
        "primary": (37, 99, 235),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Addition &",
        "title_main": "Subtraction",
        "subtitle": "Grade 1-2 Math Workbook",
        "tagline": "900+ Problems · Single & Double Digit · Answer Key",
        "ages_badge": "GRADES 1-2",
        "decorations": [],
        "features": [
            "Single & two digit addition",
            "Single & two digit subtraction",
            "Regrouping (carrying & borrowing)",
            "Mixed review pages",
            "900+ problems · full answer key",
        ],
        "perfect_for": [
            "1st-2nd grade students",
            "Homeschool math practice",
            "Daily math drills",
            "Back-to-school prep",
        ],
    },
    "number_tracing": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Number Tracing",
        "title_main": "1-100",
        "subtitle": "Pre-K & Kindergarten Workbook",
        "tagline": "Learn to Write Numbers · 4-Line Guides",
        "ages_badge": "AGES 3-6",
        "decorations": [("1", (14, 165, 233)), ("2", (245, 158, 11)),
                        ("3", (236, 72, 153)), ("4", (16, 185, 129)),
                        ("5", (124, 58, 237))],
        "features": [
            "Numbers 1-30: one full page each",
            "Numbers 31-100: count & trace pages",
            "4-line handwriting guides",
            "Traceable number outlines",
            "Independent writing practice space",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten",
            "Homeschool families",
            "Early math readiness",
            "Handwriting practice",
        ],
    },
    "telling_time": {
        "primary": (8, 145, 178),
        "accent": (245, 158, 11),
        "soft_top": (207, 250, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Telling Time",
        "title_main": "Workbook",
        "subtitle": "Learn to Read Analog Clocks",
        "tagline": "Grade 1-3 · O'Clock to 5-Minute · Answer Key",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "How to read a clock guide",
            "Read the clock practice pages",
            "Draw the clock hands pages",
            "O'clock, half, quarter, 5-minute",
            "Full answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool math practice",
            "Daily time-telling drills",
            "Teachers and tutors",
        ],
    },
    "math_kg": {
        "primary": (59, 130, 246),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (186, 230, 253),
        "bg": (252, 248, 240),
        "title_top": "Kindergarten",
        "title_main": "MATH",
        "subtitle": "Kindergarten Math Workbook",
        "tagline": "Numbers · Addition · Subtraction · Shapes",
        "ages_badge": "AGES 4-6",
        "decorations": [],
        "features": [
            "Numbers 1-20 tracing pages",
            "Count and color activities",
            "Simple addition & subtraction",
            "Shapes and counting",
            "Answer key included",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten",
            "Homeschool families",
            "Early math readiness",
            "Teachers and parents",
        ],
    },
    "money_math": {
        "primary": (22, 163, 74),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Money Math",
        "title_main": "$ ¢",
        "subtitle": "Counting US Coins Workbook",
        "tagline": "Count Coins · Make Change · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "Coin identification guide",
            "Count the coins practice",
            "Making change problems",
            "500+ money problems",
            "Full answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool math practice",
            "Real-world money skills",
            "Teachers and tutors",
        ],
    },
    "place_value": {
        "primary": (13, 148, 136),
        "accent": (245, 158, 11),
        "soft_top": (204, 251, 241),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Place Value",
        "title_main": "100s 10s 1s",
        "subtitle": "Hundreds, Tens & Ones Workbook",
        "tagline": "Base-Ten Blocks · Expanded Form · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "Place value guide & base-ten blocks",
            "Identify place value practice",
            "Expanded form practice",
            "600+ problems",
            "Full answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool math practice",
            "Number sense building",
            "Teachers and tutors",
        ],
    },
    "hundreds_chart": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (220, 252, 231),
        "bg": (252, 248, 240),
        "title_top": "Hundreds Chart",
        "title_main": "1 - 100",
        "subtitle": "Hundreds Chart Workbook 1-100",
        "tagline": "Skip Counting · Missing Numbers · Grade K-2",
        "ages_badge": "GRADES K-2",
        "decorations": [],
        "features": [
            "Complete 1-100 reference chart",
            "Color skip counting (2s, 3s, 5s, 10s)",
            "Color odd/even numbers",
            "Missing-number activities (3 levels)",
            "30 ready-to-print pages",
        ],
        "perfect_for": [
            "Kindergarten through 2nd grade",
            "Homeschool families",
            "Number sense & skip counting",
            "Ages 5-8",
        ],
    },
    "bar_graphs": {
        "primary": (59, 130, 246),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Bar Graphs",
        "title_main": "Workbook",
        "subtitle": "Bar Graphs Workbook",
        "tagline": "Read · Draw · Compare · Grade K-2",
        "ages_badge": "GRADES K-2",
        "decorations": [],
        "features": [
            "How to read a bar graph (reference)",
            "Read graphs & answer questions (5 pages)",
            "Color the bars to match data (5 pages)",
            "Compare: most, least, total, difference",
            "Complete answer key included",
        ],
        "perfect_for": [
            "K-2nd grade students",
            "Homeschool families",
            "Data & graphing foundations",
            "Ages 5-8",
        ],
    },
    "reading_comp": {
        "primary": (16, 185, 129),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Reading",
        "title_main": "Comprehension",
        "subtitle": "Reading Comprehension Workbook",
        "tagline": "12 Short Passages · Multiple-Choice · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "12 original short passages (60-80 words)",
            "3-4 multiple-choice questions each",
            "Mix of narrative & informational texts",
            "Topics: animals, science, everyday life",
            "Complete answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool families",
            "Reading comprehension building",
            "Ages 6-9",
        ],
    },
    "word_roots": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Greek & Latin",
        "title_main": "Word Roots",
        "subtitle": "Greek and Latin Roots Workbook",
        "tagline": "Learn 20 Word Roots · Build Vocabulary · Grade 3-5",
        "ages_badge": "GRADES 3-5",
        "decorations": [],
        "features": [
            "20 essential Greek & Latin roots reference",
            "Match root to meaning (3 pages)",
            "Match word to root (3 pages)",
            "Build words & word breakdown",
            "Complete answer key included",
        ],
        "perfect_for": [
            "3rd-5th grade students",
            "Homeschool families",
            "Vocabulary building & test prep",
            "Ages 8-11",
        ],
    },
    "tally_marks": {
        "primary": (124, 58, 237),
        "accent": (245, 158, 11),
        "soft_top": (237, 233, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Tally Marks",
        "title_main": "Workbook",
        "subtitle": "Tally Marks Workbook",
        "tagline": "Read · Write · Count · Survey · Grade K-2",
        "ages_badge": "GRADES K-2",
        "decorations": [],
        "features": [
            "Reference chart (1-10 tally examples)",
            "Read tally → write number",
            "Write tally marks for given numbers",
            "Survey tally charts with questions",
            "Complete answer key included",
        ],
        "perfect_for": [
            "K-2nd grade students",
            "Homeschool families",
            "Data & graphing readiness",
            "Ages 5-8",
        ],
    },
    "synonyms_antonyms": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Synonyms and",
        "title_main": "Antonyms",
        "subtitle": "Synonyms & Antonyms Workbook",
        "tagline": "Same · Opposite · Match · Choose · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "What is a synonym / antonym (reference)",
            "Match the synonyms (4 pages)",
            "Match the antonyms (4 pages)",
            "Circle the synonym / antonym (multiple choice)",
            "Sort: synonym or antonym",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool families",
            "Vocabulary building & reading comp",
            "Ages 6-9",
        ],
    },
    "even_odd": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (220, 252, 231),
        "bg": (252, 248, 240),
        "title_top": "Even and Odd",
        "title_main": "Numbers",
        "subtitle": "Even and Odd Numbers Workbook",
        "tagline": "Color · Sort · Pattern · Grade K-2",
        "ages_badge": "GRADES K-2",
        "decorations": [],
        "features": [
            "What is even / odd reference",
            "Color the even / odd numbers (6 pages)",
            "Sort into even and odd",
            "Continue the pattern activities",
            "Complete answer key included",
        ],
        "perfect_for": [
            "K-2nd grade students",
            "Homeschool families",
            "Number sense building",
            "Ages 5-8",
        ],
    },
    "calendar_workbook": {
        "primary": (59, 130, 246),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Calendar",
        "title_main": "Workbook",
        "subtitle": "Calendar Workbook",
        "tagline": "Days · Months · Dates · Seasons · K & 1st Grade",
        "ages_badge": "AGES 5-7",
        "decorations": [],
        "features": [
            "Days of the week reference & trace",
            "Months of the year reference & trace",
            "Read a real monthly calendar",
            "Today/Yesterday/Tomorrow practice",
            "Four seasons matching",
        ],
        "perfect_for": [
            "Kindergarten & 1st grade students",
            "Homeschool families",
            "Calendar concepts & time vocabulary",
            "Ages 5-7",
        ],
    },
    "counting_bills": {
        "primary": (5, 150, 105),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Counting Money",
        "title_main": "$1 $5 $10 $20",
        "subtitle": "Counting Money Bills Workbook",
        "tagline": "Bills · Make Change · Grade 2-4",
        "ages_badge": "GRADES 2-4",
        "decorations": [],
        "features": [
            "Bill identification ($1, $5, $10, $20)",
            "Count single-type & mixed bill totals",
            "Make change problems",
            "Money word problems",
            "Complete answer key included",
        ],
        "perfect_for": [
            "2nd-4th grade students",
            "Homeschool families",
            "Life-skill math & money practice",
            "Ages 7-10",
        ],
    },
    "sentence_building": {
        "primary": (16, 185, 129),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Sentence",
        "title_main": "Building",
        "subtitle": "Sentence Building Workbook",
        "tagline": "Unscramble · Fill in · Write · K-1st Grade",
        "ages_badge": "AGES 5-7",
        "decorations": [],
        "features": [
            "60+ simple sentences using K-1 sight words",
            "Unscramble word order practice",
            "Fill-in-the-blank with word bank",
            "Capital letter & period practice",
            "Build your own sentence pages",
        ],
        "perfect_for": [
            "Kindergarten & 1st grade students",
            "Homeschool families",
            "Early writing & sentence structure",
            "Ages 5-7",
        ],
    },
    "roman_numerals": {
        "primary": (124, 58, 237),
        "accent": (245, 158, 11),
        "soft_top": (237, 233, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Roman Numerals",
        "title_main": "I V X L C D M",
        "subtitle": "Roman Numerals Workbook",
        "tagline": "Learn · Convert · Practice · Grade 3-5",
        "ages_badge": "GRADES 3-5",
        "decorations": [],
        "features": [
            "Complete reference chart (I through M)",
            "Roman → Arabic conversion (4 levels)",
            "Arabic → Roman conversion (4 levels)",
            "Famous years practice (1492, 1776, etc.)",
            "Complete answer key included",
        ],
        "perfect_for": [
            "3rd-5th grade students",
            "Homeschool families",
            "Math enrichment & history",
            "Ages 8-11",
        ],
    },
    "word_problems": {
        "primary": (59, 130, 246),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Math Word",
        "title_main": "Problems",
        "subtitle": "Math Word Problems Workbook",
        "tagline": "Add · Subtract · Multiply · Divide · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "200+ story problems across 4 operations",
            "Addition & subtraction (1-2 digit)",
            "Multiplication & division (single-digit)",
            "Mixed operation review pages",
            "Complete answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool families",
            "Problem-solving & math reading",
            "Ages 6-9",
        ],
    },
    "spelling_words": {
        "primary": (236, 72, 153),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Spelling Words",
        "title_main": "100 Words",
        "subtitle": "Spelling Words Workbook",
        "tagline": "10 Themed Lists · K & 1st Grade",
        "ages_badge": "AGES 5-7",
        "decorations": [],
        "features": [
            "100 high-frequency K-1 spelling words",
            "10 themed lists (Animals, Colors, Family...)",
            "Trace and write practice per list",
            "Fill-blank & unscramble mixed reviews",
            "Complete answer key included",
        ],
        "perfect_for": [
            "Kindergarten & 1st grade students",
            "Homeschool families",
            "Weekly spelling practice",
            "Ages 5-7",
        ],
    },
    "long_vowels": {
        "primary": (16, 185, 129),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Long Vowel Sounds",
        "title_main": "Silent E · Vowel Teams",
        "subtitle": "Long Vowel Sounds Workbook",
        "tagline": "Silent E & Vowel Teams · Grade 1-2",
        "ages_badge": "GRADES 1-2",
        "decorations": [],
        "features": [
            "Silent E patterns: a_e, i_e, o_e, u_e",
            "Vowel teams: ai, ay, ee, ea, oa, ow",
            "Trace and write practice for every pattern",
            "Fill-in-the-letters & mixed review",
            "Complete answer key included",
        ],
        "perfect_for": [
            "1st & 2nd grade students",
            "Homeschool families",
            "Phonics intervention & reading",
            "Ages 6-8",
        ],
    },
    "phonics_cvc": {
        "primary": (124, 58, 237),
        "accent": (245, 158, 11),
        "soft_top": (237, 233, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Phonics CVC",
        "title_main": "Word Families",
        "subtitle": "Phonics CVC Words Workbook",
        "tagline": "Trace · Write · Read · K-1st Grade",
        "ages_badge": "AGES 5-7",
        "decorations": [],
        "features": [
            "12 essential CVC word families",
            "Trace and write practice for every word",
            "Fill-in-the-missing-letter activities",
            "Word family sorting & mixed review",
            "41 ready-to-print pages",
        ],
        "perfect_for": [
            "Kindergarten & 1st grade students",
            "Homeschool families",
            "Early reading & phonics readiness",
            "Ages 5-7",
        ],
    },
    "cursive_handwriting": {
        "primary": (236, 72, 153),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Cursive",
        "title_main": "Handwriting",
        "subtitle": "A-Z Practice Workbook",
        "tagline": "Letters, Words & Sentences · Grade 2-4",
        "ages_badge": "GRADES 2-4",
        "decorations": [],
        "features": [
            "Uppercase A-Z cursive practice (26 pages)",
            "Lowercase a-z cursive practice (26 pages)",
            "Cursive word & sentence practice",
            "4-line handwriting guides on every page",
            "70 ready-to-print pages",
        ],
        "perfect_for": [
            "2nd-4th grade students",
            "Homeschool families",
            "Penmanship & fine motor skills",
            "Ages 7-10",
        ],
    },
    "cryptogram": {
        "primary": (124, 58, 237),
        "accent": (245, 158, 11),
        "soft_top": (237, 233, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Cryptogram",
        "title_main": "50",
        "subtitle": "Famous Quotes to Decode",
        "tagline": "Adult Brain Game · Word Cipher Puzzles",
        "ages_badge": "FOR ADULTS",
        "decorations": [],
        "features": [
            "50 cryptogram puzzles (1 per page)",
            "Famous quotes: philosophy, science, art, humor",
            "Starter hint on every puzzle",
            "Complete answer key with ciphers",
            "60 ready-to-print pages",
        ],
        "perfect_for": [
            "Adult brain training & mental fitness",
            "Senior cognitive activity",
            "Travel companion",
            "Daily morning brain boost",
        ],
    },
    "dot_to_dot": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Connect the Dots",
        "title_main": "1 2 3 ... A B C",
        "subtitle": "Connect the Dots Workbook",
        "tagline": "Numbers & Alphabet Puzzles · Ages 4-9",
        "ages_badge": "AGES 4-9",
        "decorations": [],
        "features": [
            "30 dot-to-dot picture puzzles",
            "Number puzzles, easy to hard",
            "Bonus alphabet A-Z puzzles",
            "Answer key with finished pictures",
            "37 ready-to-print pages",
        ],
        "perfect_for": [
            "Kids ages 4-9",
            "Homeschool families & classrooms",
            "Counting & alphabet practice",
            "Travel & screen-free fun",
        ],
    },
    "patterns": {
        "primary": (16, 185, 129),
        "accent": (245, 158, 11),
        "soft_top": (220, 252, 231),
        "soft_bottom": (252, 231, 243),
        "bg": (252, 248, 240),
        "title_top": "Shapes & Patterns",
        "title_main": "What's Next?",
        "subtitle": "Shapes and Patterns Workbook",
        "tagline": "AB ABC AABB Patterns · Pre-K & Kindergarten",
        "ages_badge": "AGES 4-7",
        "decorations": [],
        "features": [
            "AB, ABC, AABB, ABB & AAB patterns",
            "What-comes-next circle activities",
            "Mixed pattern review pages",
            "Full answer key included",
            "49 ready-to-print pages",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten children",
            "Homeschool families",
            "Early math & logic readiness",
            "Teachers and tutors",
        ],
    },
    "counting_objects": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (254, 243, 199),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Counting",
        "title_main": "1 - 20",
        "subtitle": "Counting Workbook 1-20",
        "tagline": "Count & Write Numbers · Pre-K & Kindergarten",
        "ages_badge": "AGES 3-6",
        "decorations": [],
        "features": [
            "Count and write numbers 1-20",
            "Fun shapes to count on every page",
            "Number tracing with handwriting guides",
            "Count-and-circle & count-and-color activities",
            "32 ready-to-print pages",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten children",
            "Homeschool families",
            "Early counting & number recognition",
            "Teachers and tutors",
        ],
    },
    "skip_counting": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (219, 234, 254),
        "soft_bottom": (220, 252, 231),
        "bg": (252, 248, 240),
        "title_top": "Skip Counting",
        "title_main": "5 10 15 20",
        "subtitle": "Skip Counting Workbook",
        "tagline": "Count by 2s 3s 4s 5s 10s · Grade 1-3",
        "ages_badge": "GRADES 1-3",
        "decorations": [],
        "features": [
            "Count by 2s, 3s, 4s, 5s & 10s",
            "Fill-in-the-missing-number practice",
            "Skip counting intro for each step",
            "Mixed review pages",
            "Full answer key included",
        ],
        "perfect_for": [
            "1st-3rd grade students",
            "Homeschool math practice",
            "Multiplication readiness",
            "Teachers and tutors",
        ],
    },
    "comparing_numbers": {
        "primary": (234, 88, 12),
        "accent": (245, 158, 11),
        "soft_top": (255, 237, 213),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Greater / Less Than",
        "title_main": "> = <",
        "subtitle": "Comparing Numbers Workbook",
        "tagline": "Single to Three Digit · Grade 1-2",
        "ages_badge": "GRADES 1-2",
        "decorations": [],
        "features": [
            "Greater/less than symbol guide",
            "Single-digit comparison",
            "Two & three digit comparison",
            "800+ comparison problems",
            "Full answer key included",
        ],
        "perfect_for": [
            "1st-2nd grade students",
            "Homeschool math practice",
            "Number sense building",
            "Teachers and tutors",
        ],
    },
    "fractions": {
        "primary": (219, 39, 119),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (254, 243, 199),
        "bg": (252, 248, 240),
        "title_top": "Fractions",
        "title_main": "1/2  3/4",
        "subtitle": "Introduction to Fractions Workbook",
        "tagline": "Visual Circle & Bar Models · Grade 2-4",
        "ages_badge": "GRADES 2-4",
        "decorations": [],
        "features": [
            "Visual fraction introduction",
            "Identify the fraction practice",
            "Shade the fraction practice",
            "Circle and bar models",
            "Full answer key included",
        ],
        "perfect_for": [
            "2nd-4th grade students",
            "Homeschool math practice",
            "Visual learners",
            "Teachers and tutors",
        ],
    },
    "alphabet_prek": {
        "primary": (14, 165, 233),
        "accent": (245, 158, 11),
        "soft_top": (252, 231, 243),
        "soft_bottom": (219, 234, 254),
        "bg": (252, 248, 240),
        "title_top": "Alphabet",
        "title_main": "A-Z",
        "subtitle": "Alphabet Tracing Workbook",
        "tagline": "Uppercase · Lowercase · Letter Recognition",
        "ages_badge": "AGES 3-5",
        "decorations": [],
        "features": [
            "Uppercase A-Z tracing (26 pages)",
            "Lowercase a-z tracing (26 pages)",
            "Letter recognition activities",
            "Uppercase-lowercase matching",
            "Beginning sounds practice",
        ],
        "perfect_for": [
            "Pre-K & Kindergarten",
            "Homeschool families",
            "Early literacy practice",
            "Handwriting readiness",
        ],
    },
}


def font(size: int, bold: bool = False):
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text_w(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def draw_centered(draw, text, f, y, color, canvas_w=CANVAS_SIZE[0]):
    w = text_w(draw, text, f)
    draw.text(((canvas_w - w) // 2, y), text, font=f, fill=color)


def load_meta(book):
    return json.loads((SKILL_DIR / "references" / f"{book}_meta.json").read_text())


# ─── Thumbnails ─────────────────────────────────

def _text_at(d, text, f, cx, cy, color):
    """(cx,cy) 中心にテキスト描画。"""
    bbox = d.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    d.text((cx - w // 2, cy - h // 2 - bbox[1]), text, font=f, fill=color)


def _pdf_page(pdf_path, page_idx, zoom=2.2):
    """PDF の指定ページ（0-indexed）を PIL Image で返す。"""
    import fitz
    doc = fitz.open(str(pdf_path))
    if page_idx >= len(doc):
        page_idx = len(doc) - 1
    page = doc[page_idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def _fit(im, w, h):
    """アスペクト維持で w×h 内に収める。"""
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im


def _framed(im, border=14):
    """白フレーム付き（モックアップ感）。"""
    fr = Image.new("RGB", (im.width + border * 2, im.height + border * 2),
                   (255, 255, 255))
    fr.paste(im, (border, border))
    return fr


def make_01_cover(meta, config, out):
    """表紙：実ワークシートページのプレビューを主役に（クリーン・competitor水準）。

    リサーチ結論: 1枚目はテキスト/バッジを盛らず、商品そのもの（実ページ）を
    大きく見せる。装飾は最小限。
    """
    W, H = CANVAS_SIZE
    bg = config["bg"]
    primary = config["primary"]
    accent = config["accent"]
    DARK = (45, 45, 48)

    canvas = Image.new("RGB", CANVAS_SIZE, bg)
    d = ImageDraw.Draw(canvas)

    title = meta.get("title", "")
    subtitle = meta.get("subtitle", config.get("subtitle", ""))
    pages = meta.get("pages", 50)

    # 上部：控えめタイトル（盛らない）
    title_font = font(82, True)
    while text_w(d, title, title_font) > W - 360 and title_font.size > 44:
        title_font = font(title_font.size - 6, True)
    _text_at(d, title, title_font, W // 2, 175, DARK)
    if subtitle:
        sub = subtitle if len(subtitle) <= 56 else subtitle[:54] + "…"
        _text_at(d, sub, font(40), W // 2, 285, (110, 110, 112))
    # 細い区切り線
    d.line([(W // 2 - 280, 360), (W // 2 + 280, 360)], fill=accent, width=3)

    # 中央：実ワークシートページのプレビュー（PDF中身）を主役に
    book_dir = out.parent.parent
    pdf_path = book_dir / f"{book_dir.name}_workbook.pdf"
    placed = False
    if pdf_path.exists():
        try:
            # 後ろにサブ1枚（束感）→ 前面にメイン1枚
            sub_page = _framed(_fit(_pdf_page(pdf_path, 5), 880, 1140))
            sub_r = sub_page.convert("RGBA").rotate(
                -7, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
            canvas.paste(sub_r, (W // 2 - sub_r.width // 2 + 230, 470), sub_r)

            main_page = _framed(_fit(_pdf_page(pdf_path, 3), 980, 1280))
            # 影
            shadow = Image.new("RGBA", (main_page.width + 36, main_page.height + 36),
                               (0, 0, 0, 0))
            ImageDraw.Draw(shadow).rectangle(
                [(24, 24), (main_page.width + 24, main_page.height + 24)],
                fill=(0, 0, 0, 60))
            mx = W // 2 - main_page.width // 2 - 110
            canvas.paste(shadow, (mx - 6, 470 - 6), shadow)
            canvas.paste(main_page, (mx, 470))
            placed = True
        except Exception as e:
            print(f"  (pdf preview failed: {e})")

    if not placed:
        # フォールバック：タイトルワード大きく
        _text_at(d, config.get("title_main", ""), font(220, True),
                 W // 2, 1050, primary)

    # 右上：小さめページ数バッジ（セーフマージン内・控えめ）
    bx, by, br = W - 320, 560, 132
    d.ellipse([(bx - br, by - br), (bx + br, by + br)], fill=accent)
    _text_at(d, str(pages), font(96, True), bx, by - 26, (255, 255, 255))
    _text_at(d, "PAGES", font(40, True), bx, by + 54, (255, 255, 255))

    # 下端：細い帯（PDF / Instant Download / 学年）
    band_h = 130
    d.rectangle([(0, H - band_h), (W, H)], fill=DARK)
    _text_at(d, f"PRINTABLE PDF   ·   INSTANT DOWNLOAD   ·   {config['ages_badge']}",
             font(42, True), W // 2, H - band_h // 2, (255, 255, 255))

    canvas.save(out, "PNG")


def make_02_features_grid(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)

    draw_centered(d, "What's Inside", font(100, True), 100, color=config["primary"])
    d.rectangle([(600, 250), (1400, 260)], fill=config["accent"])

    y = 420
    for line in config["features"]:
        # チェックマーク
        d.text((250, y), "✓", font=font(70, True), fill=config["primary"])
        d.text((360, y + 5), line, font=font(60, True), fill=(31, 41, 55))
        y += 130

    canvas.save(out, "PNG")


def make_03_perfect_for(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)

    draw_centered(d, "Perfect For", font(100, True), 100, color=config["accent"])
    d.rectangle([(700, 250), (1300, 260)], fill=config["primary"])

    y = 480
    for line in config["perfect_for"]:
        d.text((300, y), "•", font=font(80, True), fill=config["accent"])
        d.text((400, y + 5), line, font=font(64), fill=(31, 41, 55))
        y += 160

    pages = meta.get("pages", 50)
    draw_centered(d, f"{pages} pages · 1 PDF · Print unlimited copies",
                  font(50), 1500, color=(80, 80, 80))

    canvas.save(out, "PNG")


def make_04_big_number(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)

    # 大きな数字
    pages = meta.get("pages", 50)
    draw_centered(d, str(pages), font(700, True), 300, color=config["primary"])
    draw_centered(d, "PAGES", font(180, True), 1080, color=(31, 41, 55))
    draw_centered(d, "of beautifully designed printable content",
                  font(42), 1300, color=(80, 80, 80))

    # 下部CTA
    d.rectangle([(400, 1500), (1600, 1700)], fill=config["accent"])
    draw_centered(d, "Instant PDF Download", font(72, True), 1555, color=(31, 41, 55))

    canvas.save(out, "PNG")


def make_05_print_at_home(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)
    draw_centered(d, "Print at Home", font(140, True), 150, color=config["accent"])
    draw_centered(d, "Any standard printer", font(56), 360, color=(31, 41, 55))
    draw_centered(d, "US Letter · 8.5 × 11 inch", font(48), 450, color=(31, 41, 55))
    draw_centered(d, "Print as many copies as you need", font(48), 540, color=(31, 41, 55))

    # アイコン風
    d.rounded_rectangle([(700, 720), (1300, 1300)], radius=40, outline=config["primary"], width=12)
    draw_centered(d, "📄", font(280), 800, color=config["primary"])
    draw_centered(d, "PDF", font(80, True), 1140, color=config["primary"])

    draw_centered(d, "For personal & single-classroom use",
                  font(42), 1450, color=(120, 120, 120))
    draw_centered(d, "Black & white = printer-friendly",
                  font(42), 1530, color=(120, 120, 120))

    canvas.save(out, "PNG")


def make_06_instant_download(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)
    pages = meta.get("pages", 50)
    d.line([(300, 480), (1700, 480)], fill=(180, 160, 140), width=3)
    draw_centered(d, "Instant", font(220, True), 530, color=config["primary"])
    draw_centered(d, "Download", font(220, True), 780, color=config["primary"])
    d.line([(300, 1080), (1700, 1080)], fill=(180, 160, 140), width=3)
    draw_centered(d, f"{pages} Pages · 1 PDF File", font(70), 1140, color=(31, 41, 55))
    draw_centered(d, "US Letter (8.5 × 11 inch)", font(52), 1240, color=(80, 80, 80))
    draw_centered(d, "Ready in seconds after purchase", font(46), 1340, color=(80, 80, 80))
    canvas.save(out, "PNG")


def make_07_summary(meta, config, out):
    canvas = Image.new("RGB", CANVAS_SIZE, config["bg"])
    d = ImageDraw.Draw(canvas)
    draw_centered(d, meta.get("title", ""), font(72, True), 100, color=config["primary"])
    draw_centered(d, config["subtitle"], font(44), 200, color=config["accent"])

    # 両カラム
    pages = meta.get("pages", 50)
    price_launch = meta.get("price_launch_usd", 4.99)

    # 左：機能リスト
    d.text((100, 400), "Features", font=font(64, True), fill=config["primary"])
    y = 500
    for line in config["features"][:5]:
        d.text((100, y), f"✓  {line}", font=font(40), fill=(31, 41, 55))
        y += 90

    # 右：価格と仕様
    d.text((1100, 400), "Details", font=font(64, True), fill=config["accent"])
    details = [
        f"Pages:   {pages}",
        f"Format:  PDF (Instant Download)",
        f"Size:    US Letter 8.5×11 in",
        f"Price:   ${price_launch}",
        f"Use:     Personal + Classroom",
    ]
    y = 500
    for line in details:
        d.text((1100, y), line, font=font(40), fill=(31, 41, 55))
        y += 90

    draw_centered(d, "Made by __YOUR_BRAND__", font(42), 1500, color=(120, 120, 120))
    draw_centered(d, "etsy.com/shop/__YOUR_SHOP__", font(36), 1560, color=config["primary"])

    canvas.save(out, "PNG")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    args = parser.parse_args()

    if args.book not in BOOK_CONFIG:
        sys.exit(f"No config for {args.book}. Add it to BOOK_CONFIG.")

    meta = load_meta(args.book)
    config = BOOK_CONFIG[args.book]
    book_dir = OUTPUT_BASE / args.book
    thumb_dir = book_dir / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating thumbnails for {args.book}...")
    make_01_cover(meta, config, thumb_dir / "01_cover.png")
    print("  01 ✓")
    make_02_features_grid(meta, config, thumb_dir / "02_grid_4.png")
    print("  02 ✓")
    make_03_perfect_for(meta, config, thumb_dir / "03_grid_4b.png")
    print("  03 ✓")
    make_04_big_number(meta, config, thumb_dir / "04_grid_6.png")
    print("  04 ✓")
    make_05_print_at_home(meta, config, thumb_dir / "05_print_at_home.png")
    print("  05 ✓")
    make_06_instant_download(meta, config, thumb_dir / "06_instant_download.png")
    print("  06 ✓")
    make_07_summary(meta, config, thumb_dir / "07_summary.png")
    print("  07 ✓")

    print(f"\nDone. Output: {thumb_dir}")


if __name__ == "__main__":
    main()
