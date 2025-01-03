# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
from msccl.language import *
from msccl.topologies import *
from msccl.language.collectives import SendRecv


def send_recv(instances):
    size = 2
    chunksperloop = 1
    topology = fully_connected(size)
    collective = SendRecv(size, chunksperloop, False)
    with MSCCLPPProgram(
        "send_recv",
        topology,
        collective,
        instances,
        protocol="LL",
        use_double_scratch_buffer=True,
    ):
        for r in range(size):
            for nghr in range(size):
                if nghr == r:
                    continue
                c = chunk(r, Buffer.input, 0)
                c.put_packet(
                    nghr,
                    "scratch",
                    1,
                    sendtb=0,
                    chan_type=ChannelType.proxy,
                    temp_buffer="scratch",
                    temp_buffer_index=0,
                )

        for r in range(size):
            c = chunk(r, "scratch", 1)
            c.copy_packet(r, Buffer.output, 0, sendtb=0)

        Json()
        Check()


parser = argparse.ArgumentParser()
parser.add_argument("instances", type=int, help="number of instances")

args = parser.parse_args()

send_recv(args.instances)
