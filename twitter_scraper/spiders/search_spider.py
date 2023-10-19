import json
from typing import Any, Iterable
from urllib.parse import quote

import scrapy
from scrapy import Request
from scrapy.http import Response

from twitter_scraper.items import Tweet


class SearchSpider(scrapy.Spider):
    name = 'search'

    def __init__(self, query, **kwargs: Any):
        self.query = query
        super().__init__(**kwargs)

    @classmethod
    def parse_entries(cls, j):
        insts = j['data']['search_by_raw_query']['search_timeline']['timeline'][
            'instructions']
        entries = []
        for inst in insts:
            for entry in inst.get('entries', [inst.get('entry')]):
                entries.append(entry)
        return entries

    @classmethod
    def parse_next_cursor(cls, j):
        entries = cls.parse_entries(j)
        for entry in entries:
            if entry.get('entryId', '') != 'cursor-bottom-0':
                continue
            return entry['content']['value']

    def make_page_url(self, cursor=None):
        url = 'https://twitter.com/i/api/graphql/lZ0GCEojmtQfiUQa5oJSEw/SearchTimeline'
        params = {
            'variables': {"rawQuery": self.query, "count": 20,
                          "querySource": "typed_query", "product": "Top"},
            'features': {
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "responsive_web_home_pinned_timelines_enabled": True,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": False,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False},
        }
        if cursor:
            params['variables']['cursor'] = cursor
        params = {k: quote(json.dumps(v)) for k, v in params.items()}
        return f'{url}?variables={params["variables"]}&features={params["features"]}'

    def start_requests(self) -> Iterable[Request]:
        yield Request(self.make_page_url(), errback=self.response_error,
                      meta={'proxy': 'http://localhost:8080'})

    def parse_tweets(self, j):
        entries = self.parse_entries(j)
        for entry in entries:
            if not entry.get('entryId', '').startswith('tweet-'):
                continue
            result = entry['content']['itemContent']['tweet_results']['result']
            result = result.get('tweet') or result
            legacy_tweet_obj = result['legacy']
            legacy_user_obj = result['core']['user_results']['result']['legacy']
            t = Tweet()
            t['user_handle'] = legacy_user_obj['screen_name']
            t['text'] = legacy_tweet_obj['full_text']
            t['replies'] = legacy_tweet_obj['reply_count']
            t['retweets'] = legacy_tweet_obj['retweet_count']
            t['favorites'] = legacy_tweet_obj['favorite_count']
            t['id'] = legacy_tweet_obj['id_str']
            t['date'] = legacy_tweet_obj['created_at']
            yield t

    def parse(self, response: Response, **kwargs: Any) -> Any:
        j = json.loads(response.text)
        yield from self.parse_tweets(j)
        if next_cursor := self.parse_next_cursor(j):
            yield response.follow(self.make_page_url(next_cursor))

    def response_error(self, error):
        print(error)
