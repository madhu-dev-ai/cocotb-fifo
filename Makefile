SIM = icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(CURDIR)/fifo.v
COCOTB_TOPLEVEL = fifo
COCOTB_TEST_MODULES = test_fifo

include $(shell cocotb-config --makefiles)/Makefile.sim