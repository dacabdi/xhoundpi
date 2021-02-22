""" GNSS client """

import asyncio

class GnssService():
    """ Gnss service """

    def __init__(self, inbound_queue, outbound_queue, gnss_client, classifier, parser_provider):
        self.inbound_queue = inbound_queue,
        self.outbound_queue = outbound_queue,
        self.gnss_client = gnss_client
        self.classifier = classifier
        self.parser_provider = parser_provider

    async def run(self):
        """ TODO
        read from gnss client
        classify message
        get parser from classification
        parse message
        enqueue into inbound queue
        """
        pass

