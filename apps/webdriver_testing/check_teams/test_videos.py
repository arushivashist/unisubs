#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import os
import filecmp
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.teams import videos_tab
from webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from webdriver_testing.pages.site_pages import watch_page
from webdriver_testing.data_factories import TeamMemberFactory
from webdriver_testing.data_factories import TeamManagerLanguageFactory
from webdriver_testing.data_factories import TeamProjectFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import VideoFactory
from webdriver_testing.data_factories import VideoUrlFactory
from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamLangPrefFactory
from webdriver_testing.data_factories import WorkflowFactory
from webdriver_testing import data_helpers
from testhelpers.views import _create_videos
from django.core import management




class TestCaseSearch(WebdriverTestCase):
    """TestSuite for searching team videos
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseSearch, cls).setUpClass()
        #management.call_command('flush', interactive=False)

        cls.data_utils = data_helpers.DataHelpers()
        cls.logger.info("Create team 'video-test' and add 1 video")

        cls.team_owner = UserFactory.create(is_partner=True)
        cls.team = TeamMemberFactory.create(
            user = cls.team_owner).team
        cls.manager_user = TeamMemberFactory(role="ROLE_ADMIN",
            team = cls.team,
            user = UserFactory()).user
        cls.videos_tab = videos_tab.VideosTab(cls)

        data = {'url': 'http://www.youtube.com/watch?v=WqJineyEszo',
                'video__title': ('X Factor Audition - Stop Looking At My '
                                'Mom Rap - Brian Bradley'),
                'type': 'Y'
               }
        cls.test_video = cls.data_utils.create_video(**data)
        subs_data = {
                'language_code': 'en',
                'subtitles': ('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.en.srt'),
                'complete': True,
                'video': cls.test_video
               }
        cls.data_utils.add_subs(**subs_data) 
        TeamVideoFactory.create(
            team=cls.team, 
            video=cls.test_video, 
            added_by=cls.manager_user)
         
        management.call_command('update_index', interactive=False)



    def test_search_title(self):
        """Team video search for title text.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('X Factor')
        self.assertTrue(self.videos_tab.video_present(self.test_video.title))

    def test_search_updated_title(self):
        """Team video search for title text after it has been updated.

        """

        #Update the video title and description (via api)
        url_part = 'videos/%s/' % self.test_video.video_id
        new_data = {'title': 'Please do not glance at my mother.',
                    'description': 'Title update for grammar and politeness.'
                   }

        
        self.data_utils.make_request(self.team_owner, 'put', 
                                     url_part, **new_data)
        #Update the solr index
        management.call_command('update_index', interactive=False)

        #Open team videos page and search for updated title text.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('mother')
        self.assertTrue(self.videos_tab.video_present(new_data['title']))


    def test_search_updated_description(self):
        """Team video search for description text after it has been updated.

        """
        #Update the video title and description (via api)
        url_part = 'videos/%s/' % self.test_video.video_id
        new_data = { 'description': 'description update for grammar and politeness.'
                   }
        self.data_utils.make_request(self.team_owner, 'put', 
                                     url_part, **new_data)

        #Update the solr index
        management.call_command('update_index', interactive=False)

        #Open team videos page and search for updated title text.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('grammar and politeness')
        self.assertTrue(self.videos_tab.video_present(self.test_video.title))


    def test_search_subs(self):
        """Team video search for subtitle text.

        """
        
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('zeus')
        self.assertTrue(self.videos_tab.video_present(self.test_video.title))

    def test_search__nonascii(self):
        """Team video search for non-ascii char strings.
 
        """
        #Search for: 日本語, by opening entering the text via javascript
        #because webdriver can't type those characters.
        self.videos_tab.open_videos_tab(self.team.slug)
        self.browser.execute_script("document.getElementsByName"
                                    "('q')[1].value='日本語'")
        self.assertTrue(self.videos_tab.video_present(self.test_video.title))

    def test_search_no_results(self):
        """Team video search returns no results.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search('TextThatShouldNOTExistOnTheVideoOrSubs')
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
                         self.videos_tab.search_no_result())

class TestCaseFilterSort(WebdriverTestCase):
    """TestSuite for searching team videos
    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseFilterSort, cls).setUpClass()
        #management.call_command('flush', interactive=False)

        cls.data_utils = data_helpers.DataHelpers()
        cls.logger.info("Create team 'video-test' and add 1 video")

        cls.team_owner = UserFactory.create(is_partner=True)
        cls.team = TeamMemberFactory.create(
            user = cls.team_owner).team
        cls.manager_user = TeamMemberFactory(role="ROLE_ADMIN",
            team = cls.team,
            user = UserFactory()).user
        cls.videos_tab = videos_tab.VideosTab(cls)
        vidurl_data = {'url': 'http://www.youtube.com/watch?v=WqJineyEszo',
                       'video__title': 'X Factor Audition - Stop Looking At My Mom Rap',
                       'type': 'Y'
                      }
        cls.test_video = cls.data_utils.create_video(**vidurl_data)
        cls.data_utils.add_subs(video=cls.test_video)
        TeamVideoFactory.create(
            team=cls.team, 
            video=cls.test_video, 
            added_by=cls.manager_user)

         
        videos = cls.data_utils.create_several_team_videos_with_subs(
            cls.team, 
            cls.manager_user)
        management.call_command('update_index', interactive=False)



    def test_filter_clear(self):
        """Clear filters.

        """
        self.videos_tab.open_videos_tab(self.team.slug)

        #Filter so that no videos are present
        self.videos_tab.sub_lang_filter(language = 'French')
        self.videos_tab.update_filters()
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())

        #Clear filters and verify videos are displayed.
        self.videos_tab.clear_filters()
        self.assertTrue(self.videos_tab.video_present('qs1-not-transback'))


    def test_filter_languages(self):
        """Filter team videos by language.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.sub_lang_filter(language = 'Russian')
        self.videos_tab.update_filters()

        self.assertTrue(self.videos_tab.video_present('qs1-not-transback'))

    def test_filter_missing_languages(self):
        """Filter team videos by language with no subtitles.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.sub_lang_filter(language = 'Portuguese', has=False)
        self.videos_tab.update_filters()

        self.assertTrue(self.videos_tab.video_present('qs1-not-transback'))

    def test_filter_no_incomplete(self):
        """Filter by language, incomplete subs are not in results. 

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.sub_lang_filter(language = ['Portuguese'])
        self.videos_tab.update_filters()

        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


    def test_sort_name_ztoa(self):
        """Sort videos on team page reverse alphabet.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.video_sort(sort_option = 'name, z-a')
        self.videos_tab.update_filters()

        self.videos_tab.videos_displayed()
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'qs1-not-transback')

    def test_sort_time_oldest(self):
        """Sort videos on team page by oldest.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.video_sort(sort_option = 'time, oldest')
        self.videos_tab.update_filters()

        self.videos_tab.videos_displayed()
        self.assertEqual(self.videos_tab.first_video_listed(), 
                         self.test_video.title)


class TestCaseProjectsAddEdit(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseProjectsAddEdit, cls).setUpClass()
        management.call_command('flush', interactive=False)
        cls.data_utils = data_helpers.DataHelpers()
        cls.videos_tab = videos_tab.VideosTab(cls)
        cls.team_owner = UserFactory.create()
        cls.logger.info('setup: Creating team Video Test')
        cls.team = TeamMemberFactory.create(user = cls.team_owner).team
 
        cls.logger.info('setup: Adding a team with 2 projects.')
        cls.project1 = TeamProjectFactory.create(team=cls.team)
        cls.project2 = TeamProjectFactory.create(team=cls.team)

        test_videos = ['jaws.mp4', 'Birds_short.oggtheora.ogg', 'fireplace.mp4']
        cls.videos_list = []
        for vid in test_videos:
            video_url = 'http://qa.pculture.org/amara_tests/%s' % vid[0]
            tv = VideoUrlFactory(url=video_url,
                                 video__title=vid).video
            v = TeamVideoFactory(video = tv, 
                                 team = cls.team,
                                 added_by = cls.team_owner,
                                 project = cls.project2).video
            cls.videos_list.append(v)
        management.call_command('update_index', interactive=False)

        cls.videos_tab.open_videos_tab(cls.team.slug)
        cls.videos_tab.log_in(cls.team_owner.username, 'password')

        cls.project1_page = ('teams/{0}/videos/?project={1}'
                        .format(cls.team.slug, cls.project1.slug))
        cls.project2_page = ('teams/{0}/videos/?project={1}'
                        .format(cls.team.slug, cls.project2.slug))


    def test_add_new(self):
        """Submit a new video for the team and assign to a project.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)
        self.videos_tab.open_page(project_page)
        self.videos_tab.add_video(
            url = 'http://www.youtube.com/watch?v=i_0DXxNeaQ0',
            project = self.project2.name)
        management.call_command('update_index', interactive=False)

        self.videos_tab.open_page(project_page)
        self.assertTrue(self.videos_tab.video_present(
            'What is up with Noises? (The Science and Mathematics'
                        ' of Sound, Frequency, and Pitch)'))


    def test_search_simple(self):
        """Peform a basic search on the project page for videos.

        """
        tv = self.videos_list[0]
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.search(tv.title)
        self.videos_tab.project_filter(project=self.project2.name)
        self.videos_tab.update_filters()
        self.assertTrue(self.videos_tab.video_present(tv.title))


    def test_remove(self):
        """Remove a video from the team project.

        """
        tv = self.videos_list[1]

        self.videos_tab.open_page(self.project2_page)
        self.videos_tab.remove_video(video = tv.title)
        self.videos_tab.search(tv.title)
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


    def test_edit_change_project(self):
        """Move a video from project2 to project 1.

        """
        tv = self.videos_list[2]
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.open_page(self.project2_page)
        self.videos_tab.edit_video(video=tv.title,
                                   project = self.project1.name)
        management.call_command('update_index', interactive=False)

        self.videos_tab.open_page(self.project1_page)
        self.assertTrue(self.videos_tab.video_present(tv.title))


class TestCaseProjectsFilter(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseProjectsFilter, cls).setUpClass()
        management.call_command('flush', interactive=False)
        cls.data_utils = data_helpers.DataHelpers()
        cls.videos_tab = videos_tab.VideosTab(cls)
        cls.team_owner = UserFactory.create()
        cls.logger.info('setup: Creating team Video Test')
        cls.team = TeamMemberFactory.create(user = cls.team_owner).team
 
        cls.manager_user = TeamMemberFactory(role="ROLE_ADMIN",
            team=cls.team,
            user = UserFactory()).user

        cls.logger.info('setup: Adding project one and project two with '
                         'workflows enabled')
        cls.project1 = TeamProjectFactory.create(
            team=cls.team,
            workflow_enabled=True,)
        
        cls.project2 = TeamProjectFactory.create(
            team=cls.team,
            workflow_enabled=True)

        data = json.load(open('apps/videos/fixtures/teams-list.json'))
        videos = _create_videos(data, [])
        for video in videos:
            TeamVideoFactory.create(
                team=cls.team, 
                video=video, 
                added_by=cls.manager_user,
                project = cls.project2)
        management.call_command('update_index', interactive=False)
        cls.videos_tab.open_videos_tab(cls.team.slug)
        cls.videos_tab.log_in(cls.manager_user.username, 'password')


    def setUp(self):
        self.videos_tab.open_videos_tab(self.team.slug)


    def test_filter_projects(self):
        """Filter video view by project.

        """
        
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.project_filter(project=self.project1.name)
        self.videos_tab.update_filters()
        time.sleep(3)
        self.assertEqual(self.videos_tab.NO_VIDEOS_TEXT, 
            self.videos_tab.search_no_result())


    def test_filter_languages(self):
        """Filter on the project page by language.

        """
        self.videos_tab.open_videos_tab(self.team.slug)
        self.videos_tab.project_filter(project=self.project2.name)
        self.videos_tab.sub_lang_filter(language = 'English')
        self.videos_tab.update_filters()
        self.assertTrue(self.videos_tab.video_present('c'))

    def test_sort_most_subtitles(self):
        """Sort on the project page by most subtitles.

        """
        project_page = 'teams/{0}/videos/?project={1}'.format(self.team.slug, 
            self.project2.slug)
        data2 = json.load(open(
            'apps/webdriver_testing/check_teams/lots_of_subtitles.json'))
        videos2 = _create_videos(data2, [])
        for video in videos2:
            TeamVideoFactory.create(
                team=self.team, 
                video=video, 
                added_by=self.manager_user,
                project = self.project2)
        management.call_command('update_index', interactive=False)
        self.videos_tab.open_page(project_page)
        self.videos_tab.video_sort(sort_option = 'most subtitles')
        self.videos_tab.update_filters()
        self.videos_tab.videos_displayed()
        self.assertEqual(self.videos_tab.first_video_listed(), 
            'lots of translations')


class TestCaseVideosDisplay(WebdriverTestCase):
    """Check actions on team videos tab that are specific to user roles.

    """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideosDisplay, cls).setUpClass()
        #management.call_command('flush', interactive=False)
        cls.data_utils = data_helpers.DataHelpers()
        cls.videos_tab = videos_tab.VideosTab(cls)
        cls.tasks_tab = TasksTab(cls)

        cls.team_owner = UserFactory.create()

        cls.logger.info('Creating team limited access: workflows enabled, '
                         'video policy set to manager and admin, '
                         'task assign policy set to manager and admin, '
                         'membership policy open.')
        cls.limited_access_team = TeamMemberFactory.create(
            team__membership_policy = 4, #open
            team__video_policy = 2, #manager and admin
            team__task_assign_policy = 20, #manager and admin
            team__workflow_enabled = True,
            user = cls.team_owner,
            ).team

        cls.videos_tab.open_page(cls.limited_access_team.slug)


    def turn_on_automatic_tasks(self):
        self.logger.info('Turning on automatic task creation')
        #Turn on task autocreation for the team.
        WorkflowFactory.create(
            team = self.limited_access_team,
            autocreate_subtitle = True,
            autocreate_translate = True,
            review_allowed = 10)

        #Add some preferred languages to the team.
        lang_list = ['en', 'ru', 'pt-br']
        for language in lang_list:
            TeamLangPrefFactory(
                team = self.limited_access_team,
                language_code = language,
                preferred = True)

    def add_some_team_videos(self):
        self.logger.info('Adding some videos to the limited access team')
        vids = self.data_utils.create_several_team_videos_with_subs(
            team = self.limited_access_team,
            teamowner = self.team_owner)
        management.call_command('update_index', interactive=False)

        return vids

    def test_contributor_no_edit(self):
        """Video policy: manager and admin; contributor sees no edit link.

        """
        vids = self.add_some_team_videos()
        self.logger.info('Adding user contributor to the team and logging in')
        #Create a user who is a contributor to the team.
        contributor = TeamMemberFactory(role="ROLE_CONTRIBUTOR",
            team = self.limited_access_team,
            user = UserFactory(username = 'contributor')).user
        self.videos_tab.log_in(contributor.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_contributor_edit_permission(self):
        """Video policy: all team members; contributor sees the edit link.

        """
        self.logger.info('setup: Setting video policy to all team members')
        self.limited_access_team.video_policy=1
        self.limited_access_team.save()


        vids = self.add_some_team_videos()
        #Create a user who is a contributor to the team.
        self.logger.info('Adding user contributor to the team and logging in')
        contributor = TeamMemberFactory(role="ROLE_CONTRIBUTOR",
            team = self.limited_access_team,
            user = UserFactory(username = 'contributor')).user
        self.videos_tab.log_in(contributor.username, 'password')

        self.logger.info('Setting video policy to all team members')
        self.limited_access_team.video_policy=1 
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_contributor_no_tasks(self):
        """Task policy: manager and admin; contributor sees no task link.

        """

        vids = self.add_some_team_videos()
        self.logger.info('Adding user contributor to the team and logging in')
        #Create a user who is a contributor to the team.
        contributor = TeamMemberFactory(role="ROLE_CONTRIBUTOR",
            team = self.limited_access_team,
            user = UserFactory(username = 'contributor')).user
        self.videos_tab.log_in(contributor.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 
                         'Tasks'))

    def test_contributor_tasks_permission(self):
        """Task policy: all team members; contributor sees the task link.

        """
        self.logger.info('setup: Setting task policy to all team members')
        self.limited_access_team.task_assign_policy=10
        self.limited_access_team.save()


        vids = self.add_some_team_videos()
        #Create a user who is a contributor to the team.
        self.logger.info('Adding user contributor to the team and logging in')
        contributor = TeamMemberFactory(role="ROLE_CONTRIBUTOR",
            team = self.limited_access_team,
            user = UserFactory(username = 'contributor')).user
        self.videos_tab.log_in(contributor.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))


    def test_manager_no_edit(self):
        """Video policy: admin only; manager sees no edit link.

        """
        self.logger.info('setup: Setting task policy to admin only')
        self.limited_access_team.video_policy=3
        self.limited_access_team.save()

        vids = self.add_some_team_videos()
        self.logger.info('Adding manager user to the team and logging in')
        #Create a user who is a manager to the team.
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'manager')).user
        self.videos_tab.log_in(manager.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_manager_edit_permission(self):
        """Video policy: manager and admin; manager sees the edit link.

        """
        vids = self.add_some_team_videos()
        self.logger.info('Adding manager user to the team and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'manager')).user
        self.videos_tab.log_in(manager.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_manager_no_tasks(self):
        """Task policy: admin only; manager sees no task link.

        """
        self.browser.delete_all_cookies()
        self.logger.info('setup: Setting task policy to admin only')
        self.limited_access_team.task_assign_policy=30
        self.limited_access_team.save()
        vids = self.add_some_team_videos()
        self.logger.info('Adding manager user to the team and logging in')
        #Create a user who is a manager to the team.
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'manager')).user
        self.videos_tab.log_in(manager.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_manager_tasks_permission(self):
        """Task policy: manager and admin; manager sees the task link.

        """

        vids = self.add_some_team_videos()
        self.logger.info('Adding manager user to the team and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'manager')).user
        self.videos_tab.log_in(manager.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_restricted_manager_no_tasks(self):
        """Task policy: manager and admin; language manager sees no task link.

        """
        vids = self.add_some_team_videos()
        self.logger.info('Adding English language manager and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'EnglishManager'))
        TeamManagerLanguageFactory(member = manager,
                                   language = 'en')
        self.videos_tab.log_in(manager.user.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_restricted_manager_tasks(self):
        """Task policy: all team members; language manager sees task link.

        """
        self.logger.info('setup: Setting task policy to all team members')
        self.limited_access_team.task_assign_policy=10
        self.limited_access_team.save()

        vids = self.add_some_team_videos()
        self.logger.info('Adding English language manager and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'EnglishManager'))
        TeamManagerLanguageFactory(member = manager,
                                   language = 'en')
        self.videos_tab.log_in(manager.user.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_restricted_manager_no_edit(self):
        """Video policy: manager and admin; language manager sees no edit link.

        """
        vids = self.add_some_team_videos()
        self.logger.info('Adding English language manager and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'EnglishManager'))
        TeamManagerLanguageFactory(member = manager,
                                   language = 'en')
        self.videos_tab.log_in(manager.user.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))


    def test_restricted_manager_edit(self):
        """Video policy: all team members; language manager sees edit link.

        """
        self.logger.info('setup: Setting video policy to all team members')
        self.limited_access_team.video_policy=1
        self.limited_access_team.save()

        vids = self.add_some_team_videos()
        self.logger.info('Adding English language manager and logging in')
        manager = TeamMemberFactory(role="ROLE_MANAGER",
            team = self.limited_access_team,
            user = UserFactory(username = 'EnglishManager'))
        TeamManagerLanguageFactory(member = manager,
                                   language = 'en')
        self.videos_tab.log_in(manager.user.username, 'password')

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Edit'))



    def test_nonmember_no_tasks(self):
        """Task policy: all team members; non-member sees no tasks. 

        """
        self.logger.info('setup: Setting task policy to all team members')
        self.limited_access_team.task_assign_policy=10
        self.limited_access_team.save()
        
        #Add some test videos to the team.
        vids = self.add_some_team_videos()
        #Create a user who is not a member 
        non_member = UserFactory(username = 'non_member')
        self.videos_tab.log_in(non_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_nonmember_no_edit(self):
        """Video policy: all team members; non-memeber sees no edit.

        """
        self.logger.info('setup: Setting video policy to all team members')
        self.limited_access_team.video_policy=1
        self.limited_access_team.save()
        
        #Add some test videos to the team.
        vids = self.add_some_team_videos()

        #Create a user who is not a member 
        non_member = UserFactory(username = 'non_member')
        self.videos_tab.log_in(non_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))


    def test_guest_no_tasks(self):
        """Task policy: all team members; guest sees no tasks. 

        """
        self.logger.info('setup: Setting task policy to all team members')
        self.limited_access_team.task_assign_policy=10
        self.limited_access_team.save()
        
        #Add some test videos to the team.
        vids = self.add_some_team_videos()

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_guest_no_edit(self):
        """Video policy: all team members; guest sees no edit.

        """
        self.logger.info('setup: Setting video policy to all team members')
        self.limited_access_team.video_policy=1
        self.limited_access_team.save()
        
        vids = self.add_some_team_videos()

        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertFalse(self.videos_tab.video_has_link(vids[0].title, 'Edit'))


    def test_admin_edit_link(self):
        """Video policy: admin only; admin sees edit link.

        """
        self.logger.info('setup: Setting video policy to admin only')
        self.limited_access_team.video_policy=3
        self.limited_access_team.save()
        vids = self.add_some_team_videos()

        #Create a user who is a team admin.
        self.logger.info('Create a team admin and log in as that user')
        admin_member = TeamMemberFactory(role="ROLE_ADMIN",
            team = self.limited_access_team,
            user = UserFactory(username = 'admin_member')).user
        self.videos_tab.log_in(admin_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Edit'))

    def test_admin_task_link(self):
        """Task policy: admin only; admin sees task link.

        """
        self.logger.info('setup: Setting task policy to admin only')
        self.limited_access_team.task_assign_policy=30
        self.limited_access_team.save()

        vids = self.add_some_team_videos()

        #Create a user who is a team admin.
        self.logger.info('Create a team admin and log in as that user')
        admin_member = TeamMemberFactory(role="ROLE_ADMIN",
            team = self.limited_access_team,
            user = UserFactory(username = 'admin_member')).user
        self.videos_tab.log_in(admin_member.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertTrue(self.videos_tab.video_has_link(vids[0].title, 'Tasks'))

    def test_task_link(self):
        """A task link opens the task page for the video.
        """

        #Turn on task autocreation for the team.
        self.turn_on_automatic_tasks()

        #Add some test videos to the team.
        vids = self.add_some_team_videos()

        test_title = vids[0].title
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.videos_tab.open_video_tasks(test_title)

        self.assertEqual(test_title, self.tasks_tab.filtered_video())

    def test_languages_no_tasks(self):
        """Without tasks, display number of completed languages for video.

        """
        #Add some test videos to the team.
        vids = self.add_some_team_videos()

        test_title = 'c'
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)

        self.assertEqual('1 language', 
            self.videos_tab.displayed_languages(test_title))

    def test_languages_automatic_tasks(self):
        """With automatic tasks, display number of needed languages for video.

        """
        self.turn_on_automatic_tasks()

        #Add some test videos to the team.
        vids = self.add_some_team_videos()

        test_title = 'c'
        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)

        self.assertEqual('3 languages needed', 
            self.videos_tab.displayed_languages(test_title))

    def test_pagination_admin(self):
        """Check number of videos displayed per page for team admin.

        """
        for x in range(50):
            TeamVideoFactory.create(
                team=self.limited_access_team, 
                video=VideoFactory.create(), 
                added_by=self.team_owner)
        management.call_command('update_index', interactive=False)

        self.videos_tab.log_in(self.team_owner.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.assertEqual(8, self.videos_tab.num_videos())

    def test_pagination_user(self):
        """Check number of videos displayed per page for team contributor.

        """
        contributor = UserFactory(username = 'contributor')
        for x in range(50):
            TeamVideoFactory.create(
                team=self.limited_access_team, 
                video=VideoFactory.create(), 
                added_by=self.team_owner)
        management.call_command('update_index', interactive=False)

        self.videos_tab.log_in(contributor.username, 'password')
        self.videos_tab.open_videos_tab(self.limited_access_team.slug)
        self.videos_tab._open_filters()
        self.assertEqual(16, self.videos_tab.num_videos())

