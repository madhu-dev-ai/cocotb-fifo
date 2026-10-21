import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


async def reset(dut):
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_write_then_read(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    assert dut.empty.value == 1, "FIFO should be empty after reset"

    # Write one value
    dut.wr_en.value = 1
    dut.din.value = 0xA5
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0

    # Read it back
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    assert dut.dout.value == 0xA5, f"Expected 0xA5, got {dut.dout.value}"

@cocotb.test()
async def test_fill_until_full(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    # Write 4 values to fill the FIFO
    for value in [0x11, 0x22, 0x33, 0x44]:
        dut.wr_en.value = 1
        dut.din.value = value
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    assert dut.full.value == 1, "FIFO should be full after 4 writes"

    # Try to write a 5th value (should be ignored)
    dut.wr_en.value = 1
    dut.din.value = 0x99
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    assert dut.full.value == 1, "FIFO should still be full"

    # Read the first value back, it should be 0x11, not 0x99
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    assert dut.dout.value == 0x11, f"Expected 0x11, got {dut.dout.value}"

@cocotb.test()
async def test_fifo_order(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    values = [0x0A, 0x0B, 0x0C]

    # Write 3 values
    for value in values:
        dut.wr_en.value = 1
        dut.din.value = value
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Read 3 values back, one at a time
    for expected in values:
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        dut.rd_en.value = 0
        await RisingEdge(dut.clk)
        assert dut.dout.value == expected, f"Expected {hex(expected)}, got {dut.dout.value}"

    assert dut.empty.value == 1, "FIFO should be empty after reading all values"

@cocotb.test()
async def test_read_all_four(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    values = [0x11, 0x22, 0x33, 0x44]

    # Fill the FIFO with 4 values
    for value in values:
        dut.wr_en.value = 1
        dut.din.value = value
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Read all 4 back
    for expected in values:
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        dut.rd_en.value = 0
        await RisingEdge(dut.clk)
        assert dut.dout.value == expected, f"Expected {hex(expected)}, got {dut.dout.value}"