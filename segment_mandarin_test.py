import pytest

pytest.importorskip("jieba")

import segment_mandarin as sm
from storage import relpath


@pytest.fixture(scope="module")
def segmenter():
    return sm.Segmenter()


def test_strip_text_removes_spaces_and_punctuation():
    assert sm.strip_text("我 知道，一家 很棒的 小店。") == "我知道一家很棒的小店"


def test_attach_particles_joins_to_previous_word():
    assert sm.attach_particles(["很棒", "的", "小店", "去", "吧"], set("的吧")) \
        == ["很棒的", "小店", "去吧"]
    # A particle at the start has nothing to join to.
    assert sm.attach_particles(["的", "确"], set("的")) == ["的", "确"]


def test_unsplit_and_character_split_answers_give_the_same_words(segmenter):
    unsplit = "我知道一家很棒的小店"             # like the MSPSEN lists now
    by_character = " ".join(unsplit)            # like the BKB-SIN lists now
    expected = ["我", "知道", "一家", "很棒的", "小店"]
    assert segmenter.words(unsplit) == expected
    assert segmenter.words(by_character) == expected


def test_user_words_are_kept_whole():
    plain = sm.Segmenter().words("他喜欢吃宫保鸡丁")
    custom = sm.Segmenter(user_words=["宫保鸡丁"]).words("他喜欢吃宫保鸡丁")
    assert "宫保鸡丁" not in plain
    assert "宫保鸡丁" in custom


def test_overrides_win():
    seg = sm.Segmenter(overrides={"患病率": "患病 率"})
    assert seg.words("患病率") == ["患病", "率"]


def write(tmp_path, text):
    path = tmp_path / "list.csv"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_rewrite_changes_only_the_answer(tmp_path, segmenter):
    src = write(tmp_path,
                "1, zh, 1, 1, a/List1-01.wav, 我知道一家很棒的小店\n"
                "1, zh, 1, 2, a/List1-02.wav, 火 车 站 有 车\n"
                "\n"
                "1, zh, 1, 3, a/List1-03.wav, 现在 很多 楼房\r\n")
    trials = sm.read_trials(src, 6)
    changes = sm.segment_trials(trials, segmenter)
    out = tmp_path / "out.csv"
    sm.write_trials(str(out), trials, changes)
    assert out.read_bytes().decode("utf-8").split("\n") == [
        "1, zh, 1, 1, a/List1-01.wav, 我 知道 一家 很棒的 小店",
        "1, zh, 1, 2, a/List1-02.wav, 火车站 有 车",
        "",
        "1, zh, 1, 3, a/List1-03.wav, 现在 很多 楼房\r",
        "",
    ]
    assert [c.status for c in changes] == ["changed", "changed", "unchanged"]


def test_alternatives_are_left_for_a_person(tmp_path, segmenter):
    src = write(tmp_path, "1, zh, 1, 1, a.wav, 他 很高兴/很开心\n")
    trials = sm.read_trials(src, 6)
    [change] = sm.segment_trials(trials, segmenter)
    assert change.new == change.old
    assert change.status.startswith("check")


def test_override_that_changes_characters_is_refused(tmp_path):
    seg = sm.Segmenter(overrides={"火车站": "汽车 站"})
    trials = sm.read_trials(write(tmp_path, "1, zh, 1, 1, a.wav, 火车站\n"), 6)
    [change] = sm.segment_trials(trials, seg)
    assert change.new == "火车站"
    assert "check" in change.status


def test_wrong_field_count_is_an_error(tmp_path):
    with pytest.raises(ValueError):
        sm.read_trials(write(tmp_path, "1, zh, a.wav, 火车站\n"), 6)


def test_review_file(tmp_path):
    path = tmp_path / "review.csv"
    sm.write_review(str(path), [sm.Change(4, "火车站有车", "火车站 有 车",
                                          "changed")])
    assert path.read_text(encoding="utf-8").splitlines() == [
        "line,status,old_answer,new_answer,old_words,new_words",
        "4,changed,火车站有车,火车站 有 车,1,3",
    ]


def test_agreement():
    scores = sm.agreement([(["火车站", "有车"], ["火车站", "有", "车"]),
                           (["我", "知道"], ["我", "知道"])])
    assert scores["precision"] == pytest.approx(2 / 3)
    assert scores["recall"] == 1.0
    assert scores["exact"] == 0.5


@pytest.mark.parametrize("name", ["azbio_mandarin", "azbio_mandarin_quiet"])
def test_matches_the_hand_split_azbio_lists(segmenter, name):
    """The AzBio Mandarin lists were split by hand; stay close to them."""
    trials = sm.read_trials(relpath("metadata", f"{name}_transcript.csv"), 6)
    pairs = [(t.answer.split(), segmenter.words(t.answer))
             for t in trials if t.answer]
    assert sm.agreement(pairs)["f1"] >= 0.9
