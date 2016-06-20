from myhdl import block, delay

def reset_on_start(clock, reset):
    reset.next = True
    yield delay(40)
    yield clock.posedge
    reset.next = False
