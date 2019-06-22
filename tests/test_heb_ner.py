import sys
import unittest

from hebner import HebNer


class TestHebNER(unittest.TestCase):
    def test_remove_punctuation(self):
        """
        Test remove exstra punctuations
        """
        hebner = HebNer();
        data = """'דג, אחד בשם ג'מיל, היה-בים. פתאום (לפתע) הוא טבע:
         כמה "נוראי ואיום". יש להגיש בג"ץ בנושא!'"""
        result = hebner.replace_hypen(data)
        result = hebner.tokenize_punctuation(result)
        expected_result = """'
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
'"""
        for line1, line2 in zip(result.split('\n'), expected_result.split('\n')):
            self.assertEqual(line1, line2)


    def test_label_lines(self):
        data = (
            ("labeled",("line","שם","שם_של_מקום","","",True,False)),
            ("labeled",("line","של","שם_של_מקום","","",False,False)),
            ("labeled",("line","מקום","שם_של_מקום","","",False,True)),
            ("unlabeled",("line","יש","","","",False,False)),
            ("labeled",("line","ארגון","שם_של_ארגון","","",True,True)),
            ("unlabeled",("line","בראשות","","","",False,False)),
            ("labeled",("line","פרטי","שם_של_אדם","","",True,False)),
            ("labeled",("line","-","שם_של_אדם","","",False,False)),
            ("labeled",("line","משפחה","שם_של_אדם","","",False,True)),
            ("labeled",("line","לא","טיטל_לא_מתוייג(ריק)","","",True,False)),
            ("labeled",("line","מתוייג","טיטל_לא_מתוייג(ריק)","","",False,True)),
            ("labeled",("line","חסר","טיטל_חסר","","",True,True)),
        )
        tag_data = (
            ("Q0","שם_של_אדם","","PER"),
            ("Q1","שם_של_מקום","","LOC"),
            ("Q2","שם_של_ארגון","","ORG"),
            ("Q3","טיטל_לא_מתוייג(ריק)","",""),
            ("Q4","כותרת","",""),
        )
        expected_result = ([
            "שם;שם_של_מקום;Q1;B-LOC",
            "של;שם_של_מקום;Q1;I-LOC",
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
        result = HebNer(moc_wikidata,{"BIOES":True}).handleLines(data,"כותרת")
        self.assertEqual(result[1], expected_result[1])
        for line1,line2 in zip(result[0],expected_result[0]):
            self.assertEqual(line1, line2)

if __name__ == '__main__':
    unittest.main()