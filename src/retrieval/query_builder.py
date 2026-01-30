from typing import Dict, List


class QueryBuilder:
    
    @staticmethod
    def build_filters_for_chart(chart: Dict[str, int]) -> List[Dict]:
        """
        Build metadata filters for all planets in a chart.
        
        In Pinecone, we want to retrieve chunks where:
        (planet=Sun AND house=10) OR (planet=Moon AND house=6) OR ...
        
        """
        filters = []
        
        for planet, house in chart.items():
            filter_dict = {
                "planet": {"$eq": planet},
                "house": {"$eq": house}
            }
            filters.append(filter_dict)
        
        return filters

    @staticmethod
    def build_or_filter(chart: Dict[str, int]) -> Dict:
        """
        Build a single OR filter combining all planet-house combinations.
        
        Args:
            chart: Dictionary mapping planet names to house numbers
            
        Returns:
            Pinecone filter dictionary with $or operator
            
        Example:
            >>> chart = {"Sun": 10, "Moon": 6}
            >>> filter = QueryBuilder.build_or_filter(chart)
            >>> print(filter)
            {
                "$or": [
                    {"$and": [{"planet": {"$eq": "Sun"}}, {"house": {"$eq": 10}}]},
                    {"$and": [{"planet": {"$eq": "Moon"}}, {"house": {"$eq": 6}}]}
                ]
            }
        """
        and_filters = []
        
        for planet, house in chart.items():
            and_filter = {
                "$and": [
                    {"planet": {"$eq": planet}},
                    {"house": {"$eq": house}}
                ]
            }
            and_filters.append(and_filter)
        
        or_filter = {"$or": and_filters}
        # print(or_filter)
        return or_filter
    
    @staticmethod
    def get_query_summary(chart: Dict[str, int]) -> str:
        """
        Get a human-readable summary of what will be queried.
        
        Args:
            chart: Dictionary mapping planet names to house numbers
            
        Returns:
            Formatted string describing the query
        """
        summary = "Pinecone Query:\n"
        summary += "=" * 50 + "\n"
        summary += f"Retrieving {len(chart)} rules:\n\n"
        
        for planet, house in sorted(chart.items()):
            summary += f"  • {planet:8s} in House {house:2d}\n"
        
        summary += "\n" + "=" * 50
        return summary
