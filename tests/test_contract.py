"""Independent finite counterexamples for the proposed Hypertime frame."""

import unittest

from hypertime import Advance, Frame, Placement, declared_precedes, project


class HypertimeContractTests(unittest.TestCase):
    def setUp(self):
        self.nodes = (Placement("origin", 0), Placement("branch-a", 1),
                      Placement("branch-b", 1), Placement("later-unlinked", 5))

    def test_forked_branches_share_an_index_without_being_each_other(self):
        frame = Frame(self.nodes, (Advance("origin", "branch-a"),
                                   Advance("origin", "branch-b")))
        self.assertTrue(declared_precedes(frame, "origin", "branch-a"))
        self.assertTrue(declared_precedes(frame, "origin", "branch-b"))
        self.assertFalse(declared_precedes(frame, "branch-a", "branch-b"))
        self.assertFalse(declared_precedes(frame, "branch-b", "branch-a"))
        self.assertFalse(declared_precedes(frame, "origin", "later-unlinked"))

    def test_axis_position_alone_does_not_make_a_path(self):
        frame = Frame(self.nodes, ())
        self.assertEqual(project(frame), (("origin", 0), ("branch-a", 1),
                                          ("branch-b", 1), ("later-unlinked", 5)))
        self.assertFalse(declared_precedes(frame, "origin", "branch-a"))
        self.assertFalse(declared_precedes(frame, "origin", "later-unlinked"))

    def test_transitive_declared_path_not_a_reverse_path(self):
        nodes = (Placement("a", 0), Placement("b", 2), Placement("c", 4))
        frame = Frame(nodes, (Advance("a", "b"), Advance("b", "c")))
        self.assertTrue(declared_precedes(frame, "a", "c"))
        self.assertFalse(declared_precedes(frame, "c", "a"))
        self.assertFalse(declared_precedes(frame, "a", "a"))

    def test_malformed_or_unbound_axis_fails(self):
        bad = (
            ((Placement("a", 0), Placement("a", 1)), ()),
            ((Placement("a", True),), ()),
            ((Placement("a", 0),), (Advance("a", "missing"),)),
            ((Placement("a", 0), Placement("b", 1)), (Advance("b", "a"),)),
            ((Placement("a", 0), Placement("b", 0)), (Advance("a", "b"),)),
            ((Placement("a", 0), Placement("b", 1)),
             (Advance("a", "b"), Advance("a", "b"))),
        )
        for nodes, edges in bad:
            with self.subTest(nodes=nodes, edges=edges), self.assertRaises(ValueError):
                Frame(nodes, edges)

    def test_absent_reality_fails_instead_of_becoming_a_hidden_root(self):
        with self.assertRaises(ValueError):
            declared_precedes(Frame(self.nodes, ()), "outside", "origin")


if __name__ == "__main__":
    unittest.main()
