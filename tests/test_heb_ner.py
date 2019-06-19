import sys
import unittest

from hebner import HebNer


class TestHebNER(unittest.TestCase):
    def test_remove_punctuation(self):
        """
        Test remove exstra punctuations
        """
        data = """
        'דג, אחד בשם ג'מיל, היה-בים. פתאום(לפתע) הוא טבע: כמה "נוראי ואיום". יש להגיש בג"ץ בנושא!'
        """
        result = hebner.HebNer.tokenize_punctuation(data)
        expected_result = """
		דג
		,
		אחד
		בשם
		ג'מיל
		,
		היה
		-
		בים
		.
		פתאום
		(
		לפתע
		)
		הוא
		טבע
		:
		כמה
		"
		נוראי
		ואיום
		"
		.
		יש
		להגיש
		בג"ץ
		בנושא
		!
		"""
        self.assertEqual(result, expected_result)

    def test_remove_punctuation(self):
        data = (
            ("labeled",("line","שם","שם_של_מקום","","","","")),
            ("labeled",("line","של","שם_של_מקום","","","","")),
            ("labeled",("line","מקום","שם_של_מקום","","","","")),
            ("unlabeled",("line","יש","","","","","")),
            ("labeled",("line","ארגון","שם_של_ארגון","","","","")),
            ("unlabeled",("line","בראשות","","","","","")),
            ("labeled",("line","פרטי","שם_של_אדם","","","","")),
            ("labeled",("line","-","שם_של_אדם","","","","")),
            ("labeled",("line","משפחה","שם_של_אדם","","","","")),
            ("labeled",("line","לא","טיטל_לא_מתוייג(ריק)","","","","")),
            ("labeled",("line","מתוייג","טיטל_לא_מתוייג(ריק)","","","","")),
            ("labeled",("line","חסר","טיטל_חסר","","","","")),
        )
        tag_data = (
            ("Q0","שם_של_אדם","","PER"),
            ("Q1","שם_של_מקום","","LOC"),
            ("Q2","שם_של_ארגון","","ORG"),
            ("Q3","טיטל_לא_מתוייג(ריק)","",""),
            ("Q4","כותרת","",""),
        )
        expected_result = ([
            "שם;שם_של_מקום;Q1;B-LOC"
            ";של;שם_של_מקום;Q1;I-LOC",
            "מקום;שם_של_מקום;Q1;E-LOC",
            "יש;;;O",
            "ארגון;שם_של_ארגון;Q2;S-ORG",
            "בראשות;;;O",
            "פרטי;שם_של_אדם;Q0;B-PER",
            "-;שם_של_אדם;Q0;I-PER",
            "משפחה;שם_של_אדם;Q0;E-PER",
            "לא;טיטל_לא_מתוייג(ריק);Q3;O",
            "מתוייג;טיטל_לא_מתוייג(ריק);Q3;O",
            "i;;;O"
        ],"Q4")

        class moc_wikidata:
            def get_entities_data_by_titles(self):
                return tag_data\

        self.buffer=True #save std output
        result = HebNer(moc_wikidata).handleLines(data,"כותרת")
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()