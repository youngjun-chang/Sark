import networkx as nx

import idaapi

from sark import CodeBlock, FlowChart, get_block_start, get_nx_graph

try:
    from sark.ui import ActionHandler

    use_new_ui = True
except:
    use_new_ui = False

COLOR_REACHABLE = 0x66EE11
COLOR_UNREACHABLE = 0x6611EE
COLOR_REACHING = 0x11EE66
COLOR_NOT_REACHING = 0x1166EE
COLOR_SOURCE = 0xEE6611
COLOR_NONE = 0xFFFFFFFF
COLOR_EXIT = 0x000048


def iter_exit_nodes(ea):
    for block in FlowChart(ea):
        # Check if there are successors
        for successor in block.next:
            break
        else:
            yield block


def clear_func(ea):
    for block in FlowChart(ea):
        block.color = COLOR_NONE


def mark_not_reaching_nodes(ea, source_color=COLOR_SOURCE, other_color=COLOR_NOT_REACHING):
    graph = get_nx_graph(ea)
    graph = graph.reverse()
    block_ea = get_block_start(ea)
    reaching = nx.descendants(graph, block_ea)

    try:
        graph_nodes_iter = graph.nodes()
    except:
        graph_nodes_iter = graph.nodes_iter()

    for node_ea in graph_nodes_iter:
        if node_ea not in reaching:
            CodeBlock(node_ea).color = other_color

    CodeBlock(ea).color = source_color


def mark_reaching_nodes(ea, source_color=COLOR_SOURCE, other_color=COLOR_REACHING):
    graph = get_nx_graph(ea)
    graph = graph.reverse()
    block_ea = get_block_start(ea)
    for descendant in nx.descendants(graph, block_ea):
        CodeBlock(descendant).color = other_color

    CodeBlock(ea).color = source_color


def mark_unreachable_nodes(ea, source_color=COLOR_SOURCE, other_color=COLOR_UNREACHABLE):
    graph = get_nx_graph(ea)
    block_ea = get_block_start(ea)
    descendants = nx.descendants(graph, block_ea)
    for block in FlowChart(ea):
        if block.start_ea not in descendants:
            block.color = other_color

    CodeBlock(ea).color = source_color


def mark_reachable_nodes(ea, source_color=COLOR_SOURCE, other_color=COLOR_REACHABLE):
    graph = get_nx_graph(ea)
    block_ea = get_block_start(ea)
    for descendant in nx.descendants(graph, block_ea):
        CodeBlock(descendant).color = other_color

    CodeBlock(ea).color = source_color


def mark_exit_nodes(ea, node_color=COLOR_EXIT):
    for block in iter_exit_nodes(ea):
        block.color = node_color


class MarkReachableNodesHandler(ActionHandler):
    TEXT = "Reachable"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)
        mark_reachable_nodes(ctx.cur_ea)


class MarkUnReachableNodesHandler(ActionHandler):
    TEXT = "Unreachable"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)
        mark_unreachable_nodes(ctx.cur_ea)


class MarkReachingNodesHandler(ActionHandler):
    TEXT = "Reaching"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)
        mark_reaching_nodes(ctx.cur_ea)


class MarkNotReachingNodesHandler(ActionHandler):
    TEXT = "Not Reaching"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)
        mark_not_reaching_nodes(ctx.cur_ea)


class MarkClearHandler(ActionHandler):
    TEXT = "Clear"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)


class MarkExits(ActionHandler):
    TEXT = "Exits"

    def _activate(self, ctx):
        clear_func(ctx.cur_ea)
        mark_exit_nodes(ctx.cur_ea)

        idaapi.msg("\n" * 2)

        for block in iter_exit_nodes(ctx.cur_ea):
            idaapi.msg("Exit at 0x{:08X}\n".format(block.start_ea))


class Hooks(idaapi.UI_Hooks):
    def populating_widget_popup(self, form, popup):
        # You can attach here.
        pass

    def finish_populating_widget_popup(self, form, popup):
        # Or here, after the popup is done being populated by its owner.

        if idaapi.get_widget_type(form) == idaapi.BWN_DISASM:
            idaapi.attach_action_to_popup(form, popup, MarkReachableNodesHandler.get_name(), "Mark/")
            idaapi.attach_action_to_popup(form, popup, MarkUnReachableNodesHandler.get_name(), "Mark/")
            idaapi.attach_action_to_popup(form, popup, MarkReachingNodesHandler.get_name(), "Mark/")
            idaapi.attach_action_to_popup(form, popup, MarkNotReachingNodesHandler.get_name(), "Mark/")
            idaapi.attach_action_to_popup(form, popup, MarkExits.get_name(), "Mark/")
            idaapi.attach_action_to_popup(form, popup, MarkClearHandler.get_name(), "Mark/")


class FunctionFlow(idaapi.plugin_t):
    flags = idaapi.PLUGIN_PROC
    comment = "Show Flow in Functions"
    help = "Show code flow inside functions"
    wanted_name = "Function Flow"
    wanted_hotkey = ""

    def init(self):
        MarkReachableNodesHandler.register()
        MarkUnReachableNodesHandler.register()
        MarkReachingNodesHandler.register()
        MarkNotReachingNodesHandler.register()
        MarkExits.register()
        MarkClearHandler.register()

        self.hooks = Hooks()
        self.hooks.hook()
        return idaapi.PLUGIN_KEEP

    def term(self):
        MarkReachableNodesHandler.unregister()
        MarkUnReachableNodesHandler.unregister()
        MarkReachingNodesHandler.unregister()
        MarkNotReachingNodesHandler.unregister()
        MarkExits.unregister()
        MarkClearHandler.unregister()

    def run(self, arg):
        pass


def PLUGIN_ENTRY():
    return FunctionFlow()














