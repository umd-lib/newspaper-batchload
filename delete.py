#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from __future__ import print_function

import argparse
from rdflib.util import from_n3
from datetime import datetime
import logging
import logging.config
from classes.pcdm import Repository
from classes.util import get_title_string
import namespaces
import requests
import sys
import yaml
from classes.exceptions import RESTAPIException

logger = logging.getLogger(__name__)


#============================================================================
# HELPER FUNCTIONS
#============================================================================

def print_header():
    '''Common header formatting.'''
    title = '|     FCREPO BATCH DELETE     |'
    bar = '+' + '='*(len(title)-2) + '+'
    spacer = '|' + ' '*(len(title)-2) + '|'
    print('\n'.join(['', bar, spacer, title, spacer, bar, '']))

def print_footer():
    print('\nScript complete. Goodbye!\n')

def test_connection(fcrepo):
    # test connection to fcrepo
    logger.debug("fcrepo.endpoint = %s", fcrepo.fullpath)
    logger.debug("fcrepo.relpath = %s", fcrepo.fullpath)
    logger.debug("fcrepo.fullpath = %s", fcrepo.fullpath)
    logger.info("Testing connection to {0}".format(fcrepo.fullpath))
    if fcrepo.is_reachable():
        logger.info("Connection successful.")
    else:
        logger.warn("Unable to connect.")
        sys.exit(1)

def get_uris_to_delete(fcrepo, uri, args):
    if args.recursive is not None:
        logger.info('Constructing list of URIs to delete')
        return fcrepo.recursive_get(uri, traverse=args.predicates)
    else:
        return fcrepo.recursive_get(uri, traverse=[])

def delete_items(fcrepo, uri_list, args):
    if args.dryrun:
        for uri in uri_list:
            for (target_uri, graph) in get_uris_to_delete(fcrepo, uri, args):
                title = get_title_string(graph)
                logger.info("Would delete {0} {1}".format(target_uri, title))
        return True

    # open transaction
    logger.info('Opening transaction')
    fcrepo.open_transaction()

    # delete item
    # (and its components, if a list of predicates to traverse was given)
    try:
        for uri in uri_list:
            for (target_uri, graph) in get_uris_to_delete(fcrepo, uri, args):
                title = get_title_string(graph)
                fcrepo.delete(target_uri)
                logger.info('Deleted resource {0} {1}'.format(target_uri, title))

        # commit transaction
        logger.info('Committing transaction')
        fcrepo.commit_transaction()
        return True

    except RESTAPIException as e:
        # if anything fails during deletion of a set of uris, attempt to
        # rollback the transaction. Failures here will be caught by the main
        # loop's exception handler and should trigger a system exit
        logger.error("Item deletion failed: {0}".format(e))
        fcrepo.rollback_transaction()
        logger.warn('Transaction rolled back.')


#============================================================================
# MAIN LOOP
#============================================================================

def main():
    '''Parse args and handle options.'''

    parser = argparse.ArgumentParser(
        description='Delete tool for Fedora 4.'
        )

    # Path to the repo config (endpoint, relpath, credentials, and WebAC paths)
    parser.add_argument('-r', '--repo',
                        help='Path to repository configuration file.',
                        action='store',
                        required=True
                        )

    # Just ping the repository to verify the connection
    parser.add_argument('-p', '--ping',
                        help='Check the connection to the repository and exit.',
                        action='store_true'
                        )

    parser.add_argument('-R', '--recursive',
                        help='Delete additional objects found by traversing the given predicate(s)',
                        action='store'
                        )

    parser.add_argument('-d', '--dryrun',
                        help='Simulate a delete without modifying the repository',
                        action='store_true'
                        )

    parser.add_argument('-f', '--file',
                        help='File containing a list of URIs to delete',
                        action='store'
                        )

    parser.add_argument('uris', nargs='*',
                        help='Zero or more repository URIs to be deleted.'
                        )

    args = parser.parse_args()

    print_header()

    # configure logging
    with open('config/logging.yml', 'r') as configfile:
        logging_config = yaml.safe_load(configfile)
        logfile = 'logs/delete.py.{0}.log'.format(
            datetime.utcnow().strftime('%Y%m%d%H%M%S')
            )
        logging_config['handlers']['file']['filename'] = logfile
        logging.config.dictConfig(logging_config)

    # Load required repository config file and create repository object
    with open(args.repo, 'r') as repoconfig:
        fcrepo = Repository(yaml.safe_load(repoconfig))
        logger.info('Loaded repo configuration from {0}'.format(args.repo))

    # "--ping" tests repository connection and exits
    if args.ping:
        test_connection(fcrepo)
        sys.exit(0)

    if args.recursive is not None:
        logger.info('Recursive delete enabled')
        manager = namespaces.get_manager()
        args.predicates = [ from_n3(p, nsm=manager) for p in args.recursive.split(',') ]
        logger.info('Deletion will traverse the following predicates: {0}'.format(
            ', '.join([ p.n3() for p in args.predicates ]))
            )

    test_connection(fcrepo)
    if args.dryrun:
        logger.info('Dry run enabled, no actual deletions will take place')

    try:
        if args.file is not None:
            with open(args.file, 'r') as uri_list:
                delete_items(fcrepo, uri_list, args)
        elif args.uris is not None:
            delete_items(fcrepo, args.uris, args)

    except RESTAPIException as e:
        logger.error(
            "Unable to commit or rollback transaction, aborting"
            )
        sys.exit(1)

    print_footer()

if __name__ == "__main__":
    main()
