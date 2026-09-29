import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_declare(self):
        state = core.new_game()
        self.assertTrue(core.declare(state, "G1", 100, False))
        self.assertFalse(core.declare(state, "G1", 100, False))

    def test_02_no_clear_banned(self):
        state = core.new_game()
        core.declare(state, "G1", 100, True)
        result = core.clear(state, "G1")
        self.assertFalse(result)

    def test_03_tax_by_value(self):
        state = core.new_game()
        core.declare(state, "G1", 100, False)
        self.assertEqual(core.tax(state, "G1"), 100)

    def test_04_cancel_returns_goods(self):
        state = core.new_game()
        core.declare(state, "G1", 100, False)
        core.inspect(state, "G1")
        state["goods"]["G1"]["held"] = True
        core.cancel_inspect(state, "G1")
        self.assertNotIn("held", state["goods"]["G1"])

    def test_05_zone_capacity(self):
        state = core.new_game()
        core.receive(state, "G1")
        core.receive(state, "G2")
        result = core.receive(state, "G3")
        self.assertFalse(result)

    def test_06_violation_once(self):
        state = core.new_game()
        core.violation(state)
        self.assertEqual(state["credit"], 90)

    def test_07_inspect_failure_no_tax(self):
        state = core.new_game()
        core.declare(state, "G1", 100, False)
        state["goods"]["G1"]["defect"] = True
        state["credit"] = 50
        result = core.inspect(state, "G1")
        self.assertFalse(result)
        self.assertEqual(state["credit"], 50)

    def test_08_load_preserves_decl(self):
        state = core.new_game()
        state["decl_id"] = 6
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["decl_id"], 6)


if __name__ == "__main__":
    unittest.main()
