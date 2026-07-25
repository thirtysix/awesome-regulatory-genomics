#!/usr/bin/env python3
"""
Bio.tools Query Script

A Python script for querying the bio.tools database using their REST API.
Supports all available API parameters as command line options.
"""

import requests
import json
import argparse
import sys
import csv
import os
from typing import Dict, List, Optional, Any
from urllib.parse import quote


class BioToolsQuery:
    """Class for querying the bio.tools database."""
    
    BASE_URL = "https://bio.tools/api/tool/"
    OPENALEX_API_URL = "https://api.openalex.org/works"
    CITATION_CACHE_FILE = "citation_cache.csv"
    OPENALEX_CACHE_DIR = "openalex"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'biotools-query-script/5.0',
            'Accept': 'application/json'
        })
        self.citation_cache = self._load_citation_cache()
        self._ensure_openalex_cache_dir()
    
    def _ensure_openalex_cache_dir(self):
        """Create OpenAlex cache directory if it doesn't exist."""
        if not os.path.exists(self.OPENALEX_CACHE_DIR):
            os.makedirs(self.OPENALEX_CACHE_DIR)
    
    def _sanitize_filename(self, identifier: str) -> str:
        """Convert DOI or other identifier to OS-friendly filename."""
        # Replace problematic characters with underscores
        sanitized = identifier.replace('/', '_').replace('\\', '_').replace(':', '_')
        sanitized = sanitized.replace('<', '_').replace('>', '_').replace('|', '_')
        sanitized = sanitized.replace('?', '_').replace('*', '_').replace('"', '_')
        # Remove any remaining problematic characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '._-')
        return sanitized

    def _get_openalex_data_by_pmid(self, pmid: str) -> Dict[str, Any]:
        """Get full OpenAlex data for a PMID, using cache or API."""
        cache_file = os.path.join(self.OPENALEX_CACHE_DIR, f"pmid_{pmid}.json")
        
        # Check if cached file exists
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cached OpenAlex data for PMID {pmid}: {e}", file=sys.stderr)
        
        # Fetch from API
        try:
            url = f"{self.OPENALEX_API_URL}?filter=ids.pmid:{pmid}"
            print(f"OpenAlex API Call: {url}", file=sys.stderr)
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenAlex response for PMID {pmid}: {len(data.get('results', []))} results", file=sys.stderr)
            
            # Cache the full response
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not cache OpenAlex data for PMID {pmid}: {e}", file=sys.stderr)
            
            return data
            
        except Exception as e:
            print(f"Warning: Could not get OpenAlex data for PMID {pmid}: {e}", file=sys.stderr)
            return {'results': []}

    def _get_openalex_data_by_doi(self, doi: str) -> Dict[str, Any]:
        """Get full OpenAlex data for a DOI, using cache or API."""
        sanitized_doi = self._sanitize_filename(doi)
        cache_file = os.path.join(self.OPENALEX_CACHE_DIR, f"doi_{sanitized_doi}.json")
        
        # Check if cached file exists
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cached OpenAlex data for DOI {doi}: {e}", file=sys.stderr)
        
        # Fetch from API
        try:
            # Clean DOI - remove https://doi.org/ prefix if present
            clean_doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
            url = f"{self.OPENALEX_API_URL}?filter=doi:{clean_doi}"
            print(f"OpenAlex API Call: {url}", file=sys.stderr)
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenAlex response for DOI {doi}: {len(data.get('results', []))} results", file=sys.stderr)
            
            # Cache the full response
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not cache OpenAlex data for DOI {doi}: {e}", file=sys.stderr)
            
            return data
            
        except Exception as e:
            print(f"Warning: Could not get OpenAlex data for DOI {doi}: {e}", file=sys.stderr)
            return {'results': []}
    
    def _load_citation_cache(self) -> Dict[str, int]:
        """Load citation cache from CSV file."""
        cache = {}
        if os.path.exists(self.CITATION_CACHE_FILE):
            try:
                with open(self.CITATION_CACHE_FILE, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cache[row['pmid']] = int(row['citation_count'])
            except Exception as e:
                print(f"Warning: Could not load citation cache: {e}", file=sys.stderr)
        return cache
    
    def _save_citation_cache(self):
        """Save citation cache to CSV file."""
        try:
            with open(self.CITATION_CACHE_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['pmid', 'citation_count'])
                for pmid, count in self.citation_cache.items():
                    writer.writerow([pmid, count])
        except Exception as e:
            print(f"Warning: Could not save citation cache: {e}", file=sys.stderr)
    
    def _get_citation_count_by_pmid(self, pmid: str) -> int:
        """Get citation count for a PMID, using cache or OpenAlex API."""
        cache_key = f"pmid_{pmid}"
        if cache_key in self.citation_cache:
            return self.citation_cache[cache_key]
        
        # Get OpenAlex data (will use cache or fetch from API)
        data = self._get_openalex_data_by_pmid(pmid)
        
        if data['results']:
            citation_count = data['results'][0].get('cited_by_count', 0)
            # Cache the result
            self.citation_cache[cache_key] = citation_count
            self._save_citation_cache()
            return citation_count
        else:
            # Cache 0 for PMIDs not found
            self.citation_cache[cache_key] = 0
            self._save_citation_cache()
            return 0

    def _get_citation_count_by_doi(self, doi: str) -> int:
        """Get citation count for a DOI, using cache or OpenAlex API."""
        cache_key = f"doi_{self._sanitize_filename(doi)}"
        if cache_key in self.citation_cache:
            return self.citation_cache[cache_key]
        
        # Get OpenAlex data (will use cache or fetch from API)
        data = self._get_openalex_data_by_doi(doi)
        
        if data['results']:
            citation_count = data['results'][0].get('cited_by_count', 0)
            # Cache the result
            self.citation_cache[cache_key] = citation_count
            self._save_citation_cache()
            return citation_count
        else:
            # Cache 0 for DOIs not found
            self.citation_cache[cache_key] = 0
            self._save_citation_cache()
            return 0
    
    def _get_publication_info_from_openalex_by_pmid(self, pmid: str) -> tuple:
        """Get title and year from OpenAlex for a PMID."""
        data = self._get_openalex_data_by_pmid(pmid)
        
        if data['results']:
            work = data['results'][0]
            title = work.get('title', 'N/A')
            
            # Extract year from publication_date
            year = 'N/A'
            pub_date = work.get('publication_date')
            if pub_date:
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', str(pub_date))
                if year_match:
                    year = year_match.group()
            
            return title, year
        
        return 'N/A', 'N/A'

    def _get_publication_info_from_openalex_by_doi(self, doi: str) -> tuple:
        """Get title and year from OpenAlex for a DOI."""
        data = self._get_openalex_data_by_doi(doi)
        
        if data['results']:
            work = data['results'][0]
            title = work.get('title', 'N/A')
            
            # Extract year from publication_date
            year = 'N/A'
            pub_date = work.get('publication_date')
            if pub_date:
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', str(pub_date))
                if year_match:
                    year = year_match.group()
            
            return title, year
        
        return 'N/A', 'N/A'
    
    def _extract_pmid_from_publication(self, pub: Dict) -> Optional[str]:
        """Extract PMID from publication entry."""
        # Check for PMID in various possible locations
        if 'pmid' in pub:
            pmid = str(pub['pmid'])
            return pmid
        
        # Check in DOI if it contains PMID format
        if 'doi' in pub and pub['doi']:
            doi = pub['doi']
            if 'pmid:' in doi.lower():
                pmid = doi.lower().split('pmid:')[1].strip()
                return pmid
        
        # Check other ID fields that might contain PMID
        if 'pmcid' in pub and pub['pmcid']:
            pmcid = pub['pmcid']
            if 'pmid:' in pmcid.lower():
                pmid = pmcid.lower().split('pmid:')[1].strip()
                return pmid
        
        return None
    
    def _extract_doi_from_publication(self, pub: Dict) -> Optional[str]:
        """Extract DOI from publication entry."""
        # Check for DOI in various possible locations
        if 'doi' in pub and pub['doi']:
            doi = str(pub['doi']).strip()
            return doi
        
        # Check in metadata if it exists
        if 'metadata' in pub and pub['metadata'] and 'doi' in pub['metadata']:
            doi = str(pub['metadata']['doi']).strip()
            return doi
        
        return None
    
    def search(self, **kwargs) -> Dict[str, Any]:
        """
        Search bio.tools database with any supported parameters.
        
        Args:
            **kwargs: Any supported API parameters
            
        Returns:
            Dictionary containing search results
        """
        params = {}
        
        # Map common parameter names to API parameter names
        param_mapping = {
            'tool_type': 'toolType',
            'operating_system': 'operatingSystem',
            'collection_id': 'collectionID',
            'topic_id': 'topicID',
            'operation_id': 'operationID',
            'data_type': 'dataType',
            'data_type_id': 'dataTypeID',
            'data_format': 'dataFormat',
            'data_format_id': 'dataFormatID',
            'input_id': 'inputID',
            'output_id': 'outputID',
            'other_id': 'otherID'
        }
        
        # Add all provided parameters - handle single values only
        # Multiple values will be handled by separate API calls
        for key, value in kwargs.items():
            if value is not None and not isinstance(value, list):
                api_key = param_mapping.get(key, key)
                # Quote multi-word terms for proper API search
                if isinstance(value, str) and ' ' in value:
                    value = f'"{value}"'
                params[api_key] = value
        
        params['format'] = 'json'
        
        try:
            # Print the API call for debugging
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{self.BASE_URL}?{query_string}"
            print(f"API Call: {full_url}", file=sys.stderr)
            
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying bio.tools: {e}", file=sys.stderr)
            return None
    
    def search_multiple_terms(self, get_all_pages: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Search with support for multiple values by making separate API calls and combining results.
        """
        # Identify parameters with multiple values
        multi_value_params = {}
        single_value_params = {}
        
        for key, value in kwargs.items():
            if isinstance(value, list) and len(value) > 1:
                multi_value_params[key] = value
            else:
                single_value_params[key] = value
        
        # If no multi-value parameters, use regular search
        if not multi_value_params:
            return self.search(**kwargs)
        
        # Generate all combinations of multi-value parameters
        all_tools = {}  # Use dict to deduplicate by biotoolsID
        
        # For now, handle one multi-value parameter at a time
        # (Could be extended for multiple multi-value params with itertools.product)
        if len(multi_value_params) == 1:
            param_key, param_values = list(multi_value_params.items())[0]
            
            for value in param_values:
                # Create search params with single value
                search_params = single_value_params.copy()
                search_params[param_key] = value
                
                print(f"Searching for {param_key}='{value}'...", file=sys.stderr)
                
                if get_all_pages:
                    # Get all pages for this search term
                    all_pages_tools = self.get_all_results(**search_params)
                    result = {'list': all_pages_tools, 'count': len(all_pages_tools)}
                else:
                    result = self.search(**search_params)
                
                if result and 'list' in result:
                    tools_found = len(result['list'])
                    print(f"  Found {tools_found} tools for '{value}'", file=sys.stderr)
                    
                    tools_added = 0
                    for tool in result['list']:
                        tool_id = tool.get('biotoolsID', '')
                        if tool_id:
                            if tool_id not in all_tools:
                                tools_added += 1
                            all_tools[tool_id] = tool
                    
                    print(f"  Added {tools_added} new tools ({tools_found - tools_added} were duplicates)", file=sys.stderr)
                else:
                    print(f"  No results for '{value}'", file=sys.stderr)
        else:
            print("Warning: Multiple multi-value parameters not fully supported yet. Using first parameter only.", file=sys.stderr)
            param_key, param_values = list(multi_value_params.items())[0]
            for value in param_values:
                search_params = single_value_params.copy()
                search_params[param_key] = value
                
                print(f"Searching for {param_key}='{value}'...", file=sys.stderr)
                
                if get_all_pages:
                    # Get all pages for this search term
                    all_pages_tools = self.get_all_results(**search_params)
                    result = {'list': all_pages_tools, 'count': len(all_pages_tools)}
                else:
                    result = self.search(**search_params)
                
                if result and 'list' in result:
                    tools_found = len(result['list'])
                    print(f"  Found {tools_found} tools for '{value}'", file=sys.stderr)
                    
                    tools_added = 0
                    for tool in result['list']:
                        tool_id = tool.get('biotoolsID', '')
                        if tool_id:
                            if tool_id not in all_tools:
                                tools_added += 1
                            all_tools[tool_id] = tool
                    
                    print(f"  Added {tools_added} new tools ({tools_found - tools_added} were duplicates)", file=sys.stderr)
                else:
                    print(f"  No results for '{value}'", file=sys.stderr)
        
        # Return combined results
        combined_results = {
            'list': list(all_tools.values()),
            'count': len(all_tools)
        }
        
        print(f"Combined results: {len(all_tools)} unique tools", file=sys.stderr)
        return combined_results
    
    def get_all_results(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get all results for a query by iterating through pages.
        
        Args:
            **kwargs: Same arguments as search() method
            
        Returns:
            List of all tools matching the query
        """
        all_tools = []
        page = 1
        
        while True:
            kwargs['page'] = page
            result = self.search(**kwargs)
            
            if not result or 'list' not in result:
                break
                
            tools = result['list']
            if not tools:
                break
                
            all_tools.extend(tools)
            
            # Check if there are more pages
            if 'next' not in result or not result['next']:
                break
                
            page += 1
            
        return all_tools
    
    def print_results(self, results: Dict[str, Any], detailed: bool = False, table_file: str = None):
        """Print search results in a formatted way."""
        if not results or 'list' not in results:
            print("No results found.")
            return
        
        tools = results['list']
        count = results.get('count', len(tools))
        
        if table_file:
            self._print_table(tools, table_file)
        else:
            print(f"Found {count} tools")
            print("-" * 50)
            
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.get('name', 'Unknown')}")
                
                if detailed:
                    print(f"   ID: {tool.get('biotoolsID', 'N/A')}")
                    print(f"   Description: {tool.get('description', 'N/A')[:100]}...")
                    print(f"   Homepage: {tool.get('homepage', 'N/A')}")
                    
                    topics = tool.get('topic', [])
                    if topics:
                        topic_terms = [t.get('term', '') for t in topics[:3]]
                        print(f"   Topics: {', '.join(topic_terms)}")
                    
                    operations = tool.get('function', [])
                    if operations:
                        op_terms = []
                        for func in operations[:2]:
                            ops = func.get('operation', [])
                            op_terms.extend([op.get('term', '') for op in ops[:2]])
                        if op_terms:
                            print(f"   Operations: {', '.join(op_terms[:3])}")
                    
                    print()
                else:
                    desc = tool.get('description', '')
                    if desc:
                        print(f"   {desc[:80]}...")
                    print()
    
    def _print_table(self, tools: List[Dict[str, Any]], table_file: str):
        """Print results in table format with name, homepage, description, and citation count."""
        print("Fetching citation counts...", file=sys.stderr)
        
        # Prepare table data
        table_data = []
        for tool in tools:
            name = tool.get('name', 'N/A')
            homepage = tool.get('homepage', 'N/A')
            
            # Get tool types
            tool_types = tool.get('toolType', [])
            tool_type_str = ','.join(tool_types) if tool_types else 'N/A'
            
            description = tool.get('description', 'N/A')
            
            # Calculate citation count from publications and collect PMIDs
            citation_count = 0
            pmids = []
            first_pub_title = 'N/A'
            first_pub_year = 'N/A'
            
            publications = tool.get('publication', [])
            
            # Get title and year from first publication if available
            if publications:
                first_pub = publications[0]
                metadata = first_pub.get('metadata') if first_pub else None
                
                # Try to get title and year from bio.tools metadata first
                if metadata:
                    first_pub_title = metadata.get('title', 'N/A')
                    
                    # Try to extract year from various fields
                    if 'date' in metadata and metadata['date']:
                        date_str = metadata['date']
                        # Extract year from date string (assume YYYY format exists)
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
                        if year_match:
                            first_pub_year = year_match.group()
                
                # If bio.tools doesn't have title/year, try to get PMID or DOI and fetch from OpenAlex
                if (first_pub_title == 'N/A' or first_pub_year == 'N/A'):
                    # Try PMID first
                    pmid = self._extract_pmid_from_publication(first_pub)
                    if pmid and pmid != 'None':
                        openalex_title, openalex_year = self._get_publication_info_from_openalex_by_pmid(pmid)
                        if first_pub_title == 'N/A':
                            first_pub_title = openalex_title
                        if first_pub_year == 'N/A':
                            first_pub_year = openalex_year
                    # If still missing data and no valid PMID, try DOI
                    if (first_pub_title == 'N/A' or first_pub_year == 'N/A'):
                        doi = self._extract_doi_from_publication(first_pub)
                        if doi:
                            print(f"Using DOI for title/year lookup: {doi}", file=sys.stderr)
                            openalex_title, openalex_year = self._get_publication_info_from_openalex_by_doi(doi)
                            if first_pub_title == 'N/A':
                                first_pub_title = openalex_title
                            if first_pub_year == 'N/A':
                                first_pub_year = openalex_year
            
            # Process all publications for PMIDs/DOIs and citations
            identifiers = []
            for pub in publications:
                pmid = self._extract_pmid_from_publication(pub)
                if pmid and pmid != 'None':
                    identifiers.append(f"pmid:{pmid}")
                    citation_count += self._get_citation_count_by_pmid(pmid)
                else:
                    # If no PMID, try DOI
                    doi = self._extract_doi_from_publication(pub)
                    if doi:
                        print(f"Using DOI for citation lookup: {doi}", file=sys.stderr)
                        identifiers.append(f"doi:{doi}")
                        citation_count += self._get_citation_count_by_doi(doi)
                    else:
                        print(f"No PMID or DOI found for publication", file=sys.stderr)
            
            identifiers_str = ','.join(identifiers) if identifiers else 'N/A'
            table_data.append([name, homepage, tool_type_str, description, first_pub_title, first_pub_year, citation_count, identifiers_str])
        
        # Prepare TSV output
        headers = ['Name', 'Homepage', 'ToolType', 'Description', 'Title', 'Year', 'Citations', 'Identifiers']
        
        if table_file == '-':
            # Output to stdout
            writer = csv.writer(sys.stdout, delimiter='\t')
            writer.writerow(headers)
            writer.writerows(table_data)
        else:
            # Output to file
            with open(table_file, 'w', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(headers)
                writer.writerows(table_data)
            print(f"Table saved to {table_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Query the bio.tools database for bioinformatics tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name "blast"
  %(prog)s --topic "Proteomics" --detailed
  %(prog)s --operation "Multiple sequence alignment"
  %(prog)s --function "transcription factor" "regulatory element prediction"
  %(prog)s --tool-type "Command-line tool" "Web application" --language "Python"
        """)
    
    # General query parameters
    parser.add_argument('--q', nargs='+', help='General query term (multiple values supported)')
    parser.add_argument('--biotools-id', help='Search by bio.tools ID')
    parser.add_argument('--name', nargs='+', help='Search by tool name (multiple values supported)')
    parser.add_argument('--homepage', help='Search by homepage URL')
    parser.add_argument('--description', nargs='+', help='Search in tool description (multiple values supported)')
    parser.add_argument('--version', help='Search by tool version')
    
    # Topic and function parameters
    parser.add_argument('--topic', nargs='+', help='Search by EDAM Topic (multiple values supported)')
    parser.add_argument('--topic-id', nargs='+', help='Search by EDAM Topic URI (multiple values supported)')
    parser.add_argument('--function', nargs='+', help='Fuzzy search over function details (multiple values supported)')
    parser.add_argument('--operation', nargs='+', help='Search by EDAM Operation (multiple values supported)')
    parser.add_argument('--operation-id', nargs='+', help='Search by EDAM Operation ID (multiple values supported)')
    
    # Data parameters
    parser.add_argument('--data-type', help='Search by input/output data type')
    parser.add_argument('--data-type-id', help='Search by data type ID')
    parser.add_argument('--data-format', help='Search by data format')
    parser.add_argument('--data-format-id', help='Search by data format ID')
    parser.add_argument('--input', help='Search by input details')
    parser.add_argument('--input-id', help='Search by input ID')
    parser.add_argument('--output', help='Search by output details')
    parser.add_argument('--output-id', help='Search by output ID')
    
    # Tool characteristics
    parser.add_argument('--tool-type', nargs='+', help='Search by tool type (multiple values supported)')
    parser.add_argument('--collection-id', help='Search by tool collection')
    parser.add_argument('--maturity', help='Search by tool maturity')
    parser.add_argument('--operating-system', nargs='+', help='Search by operating system (multiple values supported)')
    parser.add_argument('--language', nargs='+', help='Search by programming language (multiple values supported)')
    parser.add_argument('--cost', help='Search by cost')
    parser.add_argument('--license', help='Search by license')
    parser.add_argument('--accessibility', help='Search by accessibility')
    
    # Additional information
    parser.add_argument('--credit', help='Search by credit information')
    parser.add_argument('--publication', help='Search by publications')
    parser.add_argument('--link', help='Search by general links')
    parser.add_argument('--documentation', help='Search by documentation')
    parser.add_argument('--download', help='Search by download links')
    parser.add_argument('--other-id', help='Search by alternate tool IDs')
    
    # Query control parameters
    parser.add_argument('--page', type=int, default=1,
                       help='Page number (default: 1)')
    parser.add_argument('--page-size', type=int, default=25,
                       help='Results per page (default: 25)')
    parser.add_argument('--sort', 
                       help='Sort field (e.g., name, last_update)')
    
    # Output parameters
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed information for each tool')
    parser.add_argument('--all', action='store_true',
                       help='Retrieve all results (not just first page)')
    parser.add_argument('--table', nargs='?', const='results.tsv', metavar='FILE',
                       help='Output results in table format to file (default: results.tsv, use - for stdout)')
    parser.add_argument('--json', metavar='FILE',
                       help='Output raw JSON results to file (use - for stdout)')
    
    args = parser.parse_args()
    
    # Check if at least one search parameter is provided
    search_args = [
        args.q, args.biotools_id, args.name, args.homepage, args.description, 
        args.version, args.topic, args.topic_id, args.function, args.operation, 
        args.operation_id, args.data_type, args.data_type_id, args.data_format, 
        args.data_format_id, args.input, args.input_id, args.output, args.output_id,
        args.tool_type, args.collection_id, args.maturity, args.operating_system,
        args.language, args.cost, args.license, args.accessibility, args.credit,
        args.publication, args.link, args.documentation, args.download, args.other_id
    ]
    
    if not any(search_args):
        parser.error("At least one search parameter is required")
    
    biotools = BioToolsQuery()
    
    # Build search parameters dictionary
    search_params = {
        'q': args.q,
        'biotoolsID': args.biotools_id,
        'name': args.name,
        'homepage': args.homepage,
        'description': args.description,
        'version': args.version,
        'topic': args.topic,
        'topic_id': args.topic_id,
        'function': args.function,
        'operation': args.operation,
        'operation_id': args.operation_id,
        'data_type': args.data_type,
        'data_type_id': args.data_type_id,
        'data_format': args.data_format,
        'data_format_id': args.data_format_id,
        'input': args.input,
        'input_id': args.input_id,
        'output': args.output,
        'output_id': args.output_id,
        'tool_type': args.tool_type,
        'collection_id': args.collection_id,
        'maturity': args.maturity,
        'operating_system': args.operating_system,
        'language': args.language,
        'cost': args.cost,
        'license': args.license,
        'accessibility': args.accessibility,
        'credit': args.credit,
        'publication': args.publication,
        'link': args.link,
        'documentation': args.documentation,
        'download': args.download,
        'other_id': args.other_id,
        'page': args.page,
        'page_size': args.page_size,
        'sort': args.sort
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    if args.all:
        # For --all with multiple terms, get all pages for each term
        has_multi_value = any(isinstance(v, list) and len(v) > 1 for v in search_params.values())
        if has_multi_value:
            results = biotools.search_multiple_terms(get_all_pages=True, **search_params)
        else:
            tools = biotools.get_all_results(**search_params)
            results = {'list': tools, 'count': len(tools)}
    else:
        results = biotools.search_multiple_terms(get_all_pages=False, **search_params)
    
    # Handle JSON output
    if args.json:
        json_output = json.dumps(results, indent=2)
        if args.json == '-':
            print(json_output)
        else:
            with open(args.json, 'w') as f:
                f.write(json_output)
            print(f"Results saved to {args.json}")
    
    # Handle regular output (can be in addition to JSON)
    if not args.json or args.table or args.detailed:
        biotools.print_results(results, detailed=args.detailed, table_file=args.table)


if __name__ == "__main__":
    main()